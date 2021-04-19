import logging

# import functions
from flask import render_template, url_for, redirect, session, request
from flask import Blueprint
from utils.okta import OktaAdmin
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
gbac_managetrustedorigins_bp = Blueprint(
    'gbac_managetrustedorigins_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='static')


@gbac_managetrustedorigins_bp.route("/managetrustedorigins")
@apply_remote_config
@is_authenticated
def gbac_trustedorigins():
    logger.debug("gbac_trustedorigins()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    trustedorigins = okta_admin.get_trusted_origin()
    trustedoriginslist = []

    for trustedorigin in trustedorigins:
        if user_info["sub"] in trustedorigin["name"]:
            trustedoriginslist.append(trustedorigin)

    return render_template(
        "/managetrustedorigins.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        trustedorigins=trustedoriginslist)


@gbac_managetrustedorigins_bp.route("/edittrustedorigins")
@apply_remote_config
@is_authenticated
def gbac_trustedorigins_edit():
    logger.debug("gbac_trustedorigins_edit()")
    # user_info = get_userinfo()
    trustedoriginid = request.args.get('trustedoriginid')

    if trustedoriginid:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        trustedorigin = okta_admin.get_trusted_origin(id=trustedoriginid)

        return render_template(
            "/managetrustedoriginscreateupdate.html",
            templatename=get_app_vertical(),
            user_info=get_userinfo(),
            config=session[SESSION_INSTANCE_SETTINGS_KEY],
            trustedorigin=trustedorigin)
    else:
        return redirect(url_for(
            "gbac_managetrustedorigins_bp.gbac_trustedorigins",
            _external=True,
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]))


@gbac_managetrustedorigins_bp.route("/createtrustedorigins")
@apply_remote_config
@is_authenticated
def gbac_trustedorigins_create():
    logger.debug("gbac_trustedorigins_create()")

    return render_template(
        "/managetrustedoriginscreateupdate.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@gbac_managetrustedorigins_bp.route("/deletetrustedorigins")
@apply_remote_config
@is_authenticated
def gbac_trustedorigins_delete():
    logger.debug("gbac_trustedorigins_delete()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    trustedoriginid = request.args.get('trustedoriginid')
    okta_admin.delete_trusted_origin(trustedoriginid)
    message = "Trusted Origin Deleted"
    return redirect(url_for(
        "gbac_managetrustedorigins_bp.gbac_trustedorigins",
        _external=True,
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
        message=message))


@gbac_managetrustedorigins_bp.route("/createtrustedoriginsfinal")
@apply_remote_config
@is_authenticated
def gbac_trustedorigins_create_final():
    logger.debug("gbac_trustedorigins_create_final()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    trustedoriginurl = request.args.get('trustedoriginurl')
    trustedoriginid = request.args.get('id')
    trustedoriginname = request.args.get('trustedoriginname')

    if trustedoriginid is None or trustedoriginid == "":
        okta_admin.create_trusted_origin(name=trustedoriginname + "-" + user_info["sub"], origin=trustedoriginurl)
        return redirect(url_for(
            "gbac_managetrustedorigins_bp.gbac_trustedorigins",
            _external=True,
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            message="Trusted Origin Created"))
    else:
        if trustedoriginurl:
            okta_admin.update_trusted_origin(name=trustedoriginname, origin=trustedoriginurl, id=trustedoriginid)
            return redirect(url_for(
                "gbac_managetrustedorigins_bp.gbac_trustedorigins",
                _external=True,
                _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
                message="Update Complete"))

        else:
            return redirect(url_for(
                "gbac_managetrustedorigins_bp.gbac_trustedorigins",
                _external=True,
                _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
                message="Missing Redirect URL"))
