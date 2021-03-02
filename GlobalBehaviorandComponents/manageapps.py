import logging

# import functions
from flask import render_template, url_for, redirect, session, request
from flask import Blueprint
from utils.okta import OktaAdmin
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
gbac_manageapps_bp = Blueprint('gbac_manageapps_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@gbac_manageapps_bp.route("/manageapps")
@apply_remote_config
@is_authenticated
def gbac_apps():
    logger.debug("gbac_apps()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    applist = okta_admin.get_applications_by_user_id(user_info["sub"])

    return render_template(
        "/manageapps.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        applist=applist)


@gbac_manageapps_bp.route("/editapps")
@apply_remote_config
@is_authenticated
def gbac_apps_edit():
    logger.debug("gbac_apps_edit()")
    # user_info = get_userinfo()
    app_id = request.args.get('appid')

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    appinfo = okta_admin.get_applications_by_id(app_id)
    logger.debug(appinfo)

    return render_template(
        "/manageappcreateupdate.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        appid=app_id,
        appinfo=appinfo)


@gbac_manageapps_bp.route("/createapps")
@apply_remote_config
@is_authenticated
def gbac_apps_create():
    logger.debug("gbac_apps_create()")
    # user_info = get_userinfo()
    # okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    return render_template(
        "/manageappcreateupdate.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@gbac_manageapps_bp.route("/deleteapps")
@apply_remote_config
@is_authenticated
def gbac_apps_delete():
    logger.debug("gbac_apps_delete()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    app_id = request.args.get('appid')
    okta_admin.delete_application(app_id)
    message = "Application Deleted"
    return redirect(url_for("gbac_manageapps_bp.gbac_apps", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"], message=message))


@gbac_manageapps_bp.route("/updateapps")
@apply_remote_config
@is_authenticated
def gbac_apps_update():
    logger.debug("gbac_apps_update()")
    # user_info = get_userinfo()
    # okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    # app_name = request.args.get('appname')
    # app_id = request.args.get('appid')
    message = "Application Updated"
    return redirect(url_for("gbac_manageapps_bp.gbac_apps", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"], message=message))


@gbac_manageapps_bp.route("/createclientcredentialapp")
@apply_remote_config
@is_authenticated
def gbac_apps_create_cc():
    logger.debug("gbac_apps_create_cc()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    app_name = request.args.get('appname')
    create_app = okta_admin.create_clientcredential_application(app_name)
    okta_admin.assign_user_to_application(user_info["sub"], user_info["email"], create_app["id"])
    return create_app
