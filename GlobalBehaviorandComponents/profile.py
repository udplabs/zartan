import logging

# import functions
from flask import render_template, session
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
gbac_profile_bp = Blueprint('gbac_profile_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@gbac_profile_bp.route("/profile")
@is_authenticated
def profile_bp():
    logger.debug("profile_bp()")
    return render_template(
        get_app_vertical() + "/profile.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])
