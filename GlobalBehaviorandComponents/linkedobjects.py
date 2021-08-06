import logging
import json
# import functions
from flask import render_template, url_for, redirect, session, request
from flask import Blueprint
from utils.okta import OktaAdmin
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
gbac_lo_bp = Blueprint('gbac_lo_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@gbac_lo_bp.route("/linkedobjects")
@apply_remote_config
@is_authenticated
def gbac_linkedobjects():
    logger.debug("gbac_linkedobjects()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    try:
        schemas = okta_admin.get_user_schemas()
    except Exception:
        schemas = ""

    nfamily = ""
    logger.debug(schemas)
    if schemas:
        family = "["
        for schema in schemas:
            family = family + "{" + \
                "\"pname\":\"" + schema['primary']['name'] + "\"," + \
                "\"ptitle\":\"" + schema['primary']['title'] + "\"," + \
                "\"aname\":\"" + schema['associated']['name'] + "\"," + \
                "\"atitle\":\"" + schema['associated']['title'] + "\"," + \
                "\"users\": [ "

            users = okta_admin.get_linked_users(user_info['sub'], schema['associated']['name'])

            for user in users:
                userid = user['_links']['self']['href'].rsplit('/', 1)[-1]
                associateduser = okta_admin.get_user(userid)
                family = family + json.dumps(associateduser) + ","

            family = family[:-1] + "]},"

        family = family[:-1] + "]"
        nfamily = json.loads(family)

    return render_template(
        "/managelinkedobjects.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        nfamily=nfamily)


@gbac_lo_bp.route("/schemas")
@apply_remote_config
@is_authenticated
def gbac_schemas():
    logger.debug("gbac_linkedobjects()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    try:
        schemas = okta_admin.get_user_schemas()
    except Exception:
        schemas = ""

    return render_template(
        "/manageschemas.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        schemas=schemas)


@gbac_lo_bp.route("/newschemas")
@apply_remote_config
@is_authenticated
def gbac_newschemas():
    logger.debug("gbac_linkedobjects()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    try:
        schemas = okta_admin.get_user_schemas()
        message = "Schema Created"
    except Exception:
        schemas = ""
        message = "Cannot Create Schema"

    return render_template(
        "/manageschemascreate.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        schemas=schemas,
        message=message)


@gbac_lo_bp.route("/createschema", methods=["POST"])
@apply_remote_config
@is_authenticated
def gbac_createschemas():
    logger.debug("gbac_linkedobjects()")

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    ptitle = request.form.get('primarytitle')
    pname = request.form.get('primaryfieldname')
    pdesc = request.form.get('primarydescription')
    atitle = request.form.get('associatedtitle')
    aname = request.form.get('associatedfieldname')
    adesc = request.form.get('associateddescription')

    try:
        okta_admin.create_schema(pname.lower(), ptitle, pdesc, aname.lower(), atitle, adesc)
        message = "Schema Created"
    except Exception:
        message = "Cannot Create Schemas. Please contact your adminstrator."

    return redirect(url_for("gbac_lo_bp.gbac_schemas", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"], message=message))


@gbac_lo_bp.route("/deleteschemas")
@apply_remote_config
@is_authenticated
def gbac_deleteschemas():
    logger.debug("gbac_deleteschemas()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    pname = request.args.get('pname')

    okta_admin.delete_user_schemas(pname)

    message = "Schema Removed"
    return redirect(url_for("gbac_lo_bp.gbac_schemas", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"], message=message))
