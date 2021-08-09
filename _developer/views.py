import logging
import requests


from flask import render_template, session, request
from flask import jsonify, abort, url_for
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config, get_udp_ns_fieldname
from utils.okta import TokenUtil, OktaUtil, OktaAdmin
from utils.rest import RestUtil

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
developer_views_bp = Blueprint('developer_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@developer_views_bp.route("/developerhome")
@is_authenticated
def developer_home():
    logger.debug("developer_home()")
    return render_template(
        "developer/developerhome.html",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


# Required for Login Landing Page
@developer_views_bp.route("/apireport")
@is_authenticated
def developer_apireport():
    logger.debug("developer_apireport()")
    return render_template(
        "developer/apireport.html",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@developer_views_bp.route("/profile")
@is_authenticated
def developer_profile():
    logger.debug("developer_profile()")

    return render_template(
        "developer/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@developer_views_bp.route("/manage-apps")
@is_authenticated
def developer_manage_api():
    logger.debug("developer_manage_apps()")

    return render_template(
        "/developer/manage_apps.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


tasks = [
    {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, Pizza, Cheese",
        'done': False
    },
    {
        "id": 2,
        "title": "Learn python",
        "description": "Gotta find a proper book or article set.",
        'done': False

    }
]


def make_public_task(task):
    new_task = {}
    for field in task:
        if field == "id":
            new_task[field] = task[field]
            new_task["uri"] = url_for(
                "developer_views_bp.get_task",
                task_id=task["id"],
                _external=True,
                _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])
        else:
            new_task[field] = task[field]
    return new_task


@developer_views_bp.route("/api")
@is_authenticated
def developer_api():
    logger.debug("developer_api()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_info = get_userinfo()
    user_info2 = okta_admin.get_user(user_info["sub"])

    try:
        production = user_info2["profile"][get_udp_ns_fieldname("production")]
    except Exception:
        logger.debug(user_info2)
        production = "false"
    return render_template(
        "developer/api.html",
        user_info=user_info,
        user_info2=user_info2,
        production=production,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@developer_views_bp.route('/api/openapi.json', methods=['GET'])
def get_apijson():
    return render_template(
        "developer/openapi.json",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@developer_views_bp.route('/api/proxy/', methods=['Post'])
def api_proxy():
    authorization = request.form.get('Authorization')
    url = request.form.get('url')
    secret = request.form.get('secret')
    key = request.form.get('key')
    tid = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description')
    done = request.form.get('done')

    api_headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {0}".format(OktaUtil.get_encoded_auth(key, secret))
    }
    introspecturl = "{issuer}/v1/introspect?token={token}".format(issuer=session[SESSION_INSTANCE_SETTINGS_KEY]["issuer"], token=authorization)
    body = {}
    accesstoken = RestUtil.execute_post(introspecturl, body, headers=api_headers)

    if "error" not in accesstoken:
        if accesstoken["active"]:
            authorization_info = TokenUtil.get_claims_from_token(authorization)
            scopes = authorization_info["scp"]
        else:
            return {"Issue": "Unauthorized"}
    else:
        return {"Issue": "Unauthorized"}

    apiresponse = check_task_event(url=url, tid=tid, title=title, description=description, done=done, scopes=scopes)

    if not apiresponse:
        apiresponse = {"Issue": "Error when processing request. Please check your values."}
    return apiresponse


def check_task_event(url, tid, title, description, done, scopes):
    apiresponse = {"Issue": "Missing Scope or Missing Data"}

    if "developer/api/tasks/" in url:
        logger.debug("get_tasks")
        if "read" in scopes:
            apiresponse = get_tasks()

    elif tid and done is None:
        logger.debug("get_singletask")
        if "read" in scopes:
            task = get_s_task(tid)
            apiresponse = jsonify({"task": task})

    elif title and done is None:
        logger.debug("create_task")
        if "write" in scopes:
            task = {
                "id": tasks[-1]['id'] + 1,
                "title": title,
                "description": description,
                "done": False
            }
            tasks.append(task)
            apiresponse = jsonify({"task": task})

    elif done:
        logger.debug("update_task")
        if "write" in scopes:
            task = get_s_task(tid)
            if task:
                task["title"] = title
                task["description"] = description
                task['done'] = done
                apiresponse = task
            else:
                apiresponse = None

    return apiresponse


def get_s_task(task_id):
    foundtask = None
    if task_id:
        for task in tasks:
            if int(task_id) == int(task['id']):
                foundtask = task
    else:
        foundtask = None

    if not foundtask:
        foundtask = None

    return foundtask


@developer_views_bp.route('/api/tasks/', methods=['GET'])
def get_tasks():
    logger.debug("get_tasks")
    alltasks = jsonify({'tasks': [make_public_task(task) for task in tasks]})
    return alltasks


@developer_views_bp.route('/api/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    logger.debug("get_tasks(tid)")
    foundtask = None
    for task in tasks:
        if int(task_id) == int(task['id']):
            foundtask = task
    if not foundtask:
        abort(404)

    return foundtask


@developer_views_bp.route('/api/task/', methods=['POST'])
def create_task():
    logger.debug(request.json)
    if not any([request.json, 'title' in request.json]):
        abort(400)
    task = {
        "id": tasks[-1]['id'] + 1,
        "title": request.json["title"],
        "description": request.json.get("description", ""),
        "done": False
    }
    tasks.append(task)
    return jsonify({"task": task}), 201


@developer_views_bp.route('/api/task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]
    if not task:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json:
        abort(400)
    if 'description' in request.json:
        abort(400)
    if 'done' in request.json and type(request.json["done"]) is not bool:
        abort(400)

    task[0]["title"] = request.json.get('title', task[0]["title"])
    task[0]["description"] = request.json.get("description", task[0]["description"])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@developer_views_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


def execute_post(url, body=None, headers=None):
    rest_response = requests.post(url, headers=headers, data=body)
    return RestUtil.handle_response_as_json(rest_response)


@developer_views_bp.route('/authorize', methods=['POST'])
@apply_remote_config
def auth_api():
    secret = request.form.get('secret')
    key = request.form.get('key')
    scopes = request.form.get('scopes')

    api_headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {0}".format(OktaUtil.get_encoded_auth(key, secret))
    }

    url = "{issuer}/v1/token".format(issuer=session[SESSION_INSTANCE_SETTINGS_KEY]["issuer"])
    body = "grant_type=client_credentials&scope={scopes}".format(scopes=scopes)
    return execute_post(url=url, body=body, headers=api_headers)
