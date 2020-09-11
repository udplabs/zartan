import logging

# import functions

from flask import render_template, session
from flask import Blueprint
from utils.okta import OktaAdmin
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
gbac_userapps_bp = Blueprint('gbac_userapps_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@gbac_userapps_bp.route("/userapps")
@apply_remote_config
@is_authenticated
def gbac_userapps_mfa():
    logger.debug("gbac_userapps_mfa()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    app_info = okta_admin.get_applications_by_user_id(user["id"])

    return render_template(
        "/userapps.html",
        user_info=get_userinfo(),
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        applist=app_info)
