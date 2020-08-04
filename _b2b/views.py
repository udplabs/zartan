import json
import logging

# import functions
from flask import render_template, session, request, redirect, url_for
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, get_udp_ns_fieldname
from utils.okta import TokenUtil, OktaAdmin
from utils.email import Email

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
b2b_views_bp = Blueprint('b2b_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@b2b_views_bp.route("/profile")
@is_authenticated
def b2b_profile():
    logger.debug("b2b_profile()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    app_info = okta_admin.get_applications_by_user_id(user["id"])

    return render_template(
        "{0}/profile.html".format(get_app_vertical()),
        templatename=get_app_vertical(),
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        applist=app_info)


@is_authenticated
@b2b_views_bp.route("/workflow-requests", methods=["GET"])
def b2b_requests_get():
    logger.debug("workflow_requests_get()")

    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    user_id = user["id"]

    if get_udp_ns_fieldname("access_requests") in user["profile"]:
        pendingRequest = user["profile"][get_udp_ns_fieldname("access_requests")]
    else:
        pendingRequest = []

    # On a GET display the registration page with the defaults
    applist = []
    list_group_full = []
    # Find the groups the user belongs to
    get_user_groups_response = okta_admin.get_user_groups(user_id=user_id)
    CONFIG_GROUP_B2B_STARTSWITH = get_udp_ns_fieldname("b2b")

    for item in get_user_groups_response:
        logging.debug(item)
        if item["profile"]["name"].startswith(CONFIG_GROUP_B2B_STARTSWITH):

            group_id = "{id}".format(id=item["id"])
            applist.append(item["profile"]["name"].replace(CONFIG_GROUP_B2B_STARTSWITH, ""))

    logging.debug(applist)
    get_groups = okta_admin.get_groups_by_name(get_udp_ns_fieldname(""))
    for item in get_groups:
        if item["profile"]["name"].startswith(CONFIG_GROUP_B2B_STARTSWITH):
            if item["profile"]["name"].replace(CONFIG_GROUP_B2B_STARTSWITH, "") not in applist:
                logging.debug(item["profile"]["name"])
                group_id = "{id}".format(id=item["id"])
                list_group_full.append({
                    "id": item["id"],
                    "name": item["profile"]["name"],
                    "description": item["profile"]["description"],
                    "status": "Pending" if group_id in pendingRequest else "Not Requested"
                })

    return render_template(
        "{0}/workflow-requests.html".format(get_app_vertical()),
        templatename=get_app_vertical(),
        user_info=user_info,
        workflow_list=list_group_full,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@is_authenticated
@b2b_views_bp.route("/workflow-requests", methods=["POST"])
def b2b_requests_post():
    logger.debug("workflow_requests_post()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    user_id = user["id"]
    if get_udp_ns_fieldname("access_requests") in user["profile"]:
        pendingRequest = user["profile"][get_udp_ns_fieldname("access_requests")]
    else:
        pendingRequest = []

    if request.form.get("request_access"):
        group_id = request.form.get("request_access")
        if group_id not in pendingRequest:
            pendingRequest.append(group_id)

        # Remove user attribute organization ( as the request has been rejected)
        # organization": "[ '{id}' ]".format(id=request.form.get('location'))
        user_data = {
            "profile": {
                get_udp_ns_fieldname("access_requests"): pendingRequest
            }
        }
        okta_admin.update_user(user_id=user_id, user=user_data)
        b2bEmailServices().emailWorkFlowRequest(group_id)

    return redirect(url_for("b2b_views_bp.b2b_requests_get", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]))


@b2b_views_bp.route("/workflow-approvals", methods=["GET"])
@is_authenticated
def b2b_approvals_get():
    logger.debug("workflow_approvals()")

    workflow_list = []
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    user_groups = okta_admin.get_user_groups(user["id"])

    user_get_response = okta_admin.get_user_list_by_search(
        'profile.{0} pr  '.format(get_udp_ns_fieldname("access_requests")))
    for list in user_get_response:
        for grp in list["profile"][get_udp_ns_fieldname("access_requests")]:
            group_get_response = okta_admin.get_group(id=grp)
            logging.debug(group_get_response)
            var = {
                "requestor": list["profile"]["login"],
                "request": group_get_response["profile"]["description"],
                "usr_grp": {"user_id": list["id"], "group_id": grp}
            }
            for clist in user_groups:
                if grp == clist['id']:
                    workflow_list.append(var)

    return render_template(
        "{0}/workflow-approvals.html".format(get_app_vertical()),
        templatename=get_app_vertical(),
        workflow_list=workflow_list,
        user_info=user_info,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@b2b_views_bp.route("/workflow-approvals", methods=["POST"])
@is_authenticated
def b2b_approvals_post():
    logger.debug("workflow_approvals()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    user_id = user["id"]

    if request.form.get("action") == "reject":
        req = request.form.get("action_value")
        req = req.replace("\'", "\"")
        req = json.loads(req)
        user_id = req["user_id"]
        group_id = req["group_id"]
        user_wf = okta_admin.get_user(user_id)

        grps = user_wf["profile"][get_udp_ns_fieldname("access_requests")]
        grps.remove(group_id)

        # Remove user attribute organization ( as the request has been rejected)
        user_data = {
            "profile": {
                get_udp_ns_fieldname("access_requests"): grps
            }
        }
        okta_admin.update_user(user_id=user_id, user=user_data)

    if request.form.get("action") == "approve":
        req = request.form.get("action_value")
        req = req.replace("\'", "\"")
        req = json.loads(req)
        user_id = req["user_id"]
        group_id = req["group_id"]

        # Assign user to group
        okta_admin.assign_user_to_group(group_id, user_id)

        user_wf = okta_admin.get_user(user_id)

        grps = user_wf["profile"][get_udp_ns_fieldname("access_requests")]
        grps.remove(group_id)

        # Remove user attribute organization ( as the request has been rejected)
        user_data = {
            "profile": {
                get_udp_ns_fieldname("access_requests"): grps
            }
        }
        okta_admin.update_user(user_id=user_id, user=user_data)

    return redirect(url_for("b2b_views_bp.b2b_approvals_get", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]))


# Class containing email services and formats
class b2bEmailServices:

    # EMail workflow Request to the Admin
    def emailWorkFlowRequest(self, group_id):
        logger.debug("emailWorkFlowRequest()")
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

        activation_link = url_for("b2b_views_bp.b2b_approvals_get", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])
        # Send Activation Email to the Admin
        subject_admin = "A workflow request was received"
        message_admin = """
            A new request for access was received. The request is awaiting your approval. <br /> <br />
            Click this link to log into your account and review the request<br /><br />
            <a href='{activation_link}'>{activation_link}</a>"
            """.format(activation_link=activation_link)

        # Find All members that will be notified
        recipients = []
        user_list = okta_admin.get_user_list_by_group_id(group_id)
        for user in user_list:
            recipients.append({"address": user["profile"]["email"]})

        if recipients:
            email_send = Email.send_mail(subject=subject_admin, message=message_admin, recipients=recipients)
            return email_send
        else:
            return ''
