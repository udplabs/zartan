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
    myapplist = []
    for app in applist:
        if ("profile" in app) and ("createdby" in app["profile"]) and (user_info["email"] in app["profile"]["createdby"]):
            myapplist.append(app)

    return render_template(
        "/manageapps.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        applist=myapplist)


@gbac_manageapps_bp.route("/manageapis")
@apply_remote_config
@is_authenticated
def gbac_apis():
    logger.debug("gbac_apps()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    applist = okta_admin.get_applications_by_user_id(user_info["sub"])
    myapplist = []
    for app in applist:
        if ("profile" in app) and ("createdby" in app["profile"]) and (user_info["email"] in app["profile"]["createdby"]):
            myapplist.append(app)

    return render_template(
        "/manageapis.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        applist=myapplist)


@gbac_manageapps_bp.route("/editapps")
@apply_remote_config
@is_authenticated
def gbac_apps_edit():
    logger.debug("gbac_apps_edit()")
    # user_info = get_userinfo()
    app_id = request.args.get('appid')

    if app_id:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        appinfo = okta_admin.get_applications_by_id(app_id)

        return render_template(
            "/manageappscreateupdate.html",
            templatename=get_app_vertical(),
            user_info=get_userinfo(),
            config=session[SESSION_INSTANCE_SETTINGS_KEY],
            appid=app_id,
            appinfo=appinfo)
    else:
        return redirect(url_for("gbac_manageapps_bp.gbac_apps", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]))


@gbac_manageapps_bp.route("/editapis")
@apply_remote_config
@is_authenticated
def gbac_apis_edit():
    logger.debug("gbac_apps_edit()")
    # user_info = get_userinfo()
    app_id = request.args.get('appid')

    if app_id:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        appinfo = okta_admin.get_applications_by_id(app_id)

        return render_template(
            "/manageapiscreateupdate.html",
            templatename=get_app_vertical(),
            user_info=get_userinfo(),
            config=session[SESSION_INSTANCE_SETTINGS_KEY],
            appid=app_id,
            appinfo=appinfo)
    else:
        return redirect(url_for("gbac_manageapps_bp.gbac_apis", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]))


@gbac_manageapps_bp.route("/createapps")
@apply_remote_config
@is_authenticated
def gbac_apps_createApp():
    logger.debug("gbac_apps_createApp()")
    # user_info = get_userinfo()
    # okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    return render_template(
        "/manageappscreateupdate.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@gbac_manageapps_bp.route("/createapis")
@apply_remote_config
@is_authenticated
def gbac_apps_createAPI():
    logger.debug("gbac_apps_createAPI()")
    # user_info = get_userinfo()
    # okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    return render_template(
        "/manageapiscreateupdate.html",
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
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    oidcclientid = request.args.get('oidcclientid')
    oidcloginredirecturi = request.args.get('oidcloginredirecturi')
    oidcapplabel = request.args.get('oidcapplabel')

    if oidcclientid != "" and oidcloginredirecturi != "" and oidcapplabel != "":
        okta_admin.update_web_application(app_label=oidcapplabel, redirect_uris=oidcloginredirecturi, app_id=oidcclientid)
        return redirect(url_for(
            "gbac_manageapps_bp.gbac_apps",
            _external=True,
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            message="Application Updated"))
    else:
        return "", 500


@gbac_manageapps_bp.route("/createclientcredentialapp")
@apply_remote_config
@is_authenticated
def gbac_apps_create_cc():
    logger.debug("gbac_apps_create_cc()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    app_name = request.args.get('appname')
    create_app = okta_admin.create_clientcredential_application(app_name=app_name, createdby=user_info["email"])
    okta_admin.assign_user_to_application(user_info["sub"], user_info["email"], create_app["id"])
    return create_app


@gbac_manageapps_bp.route("/createoidcapp")
@apply_remote_config
@is_authenticated
def gbac_apps_create_oidc():
    logger.debug("gbac_apps_create_oidc()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    app_name = request.args.get('appname')
    redirecturi = request.args.get('loginredirecturi')
    create_app = okta_admin.create_web_application(app_name=app_name, redirect_uris=redirecturi, createdby=user_info["email"])
    okta_admin.assign_user_to_application(user_info["sub"], user_info["email"], create_app["id"])
    return create_app
