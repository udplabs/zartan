import logging

# import functions
from flask import render_template, session
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
admin_views_bp = Blueprint('admin_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@admin_views_bp.route("/adminhome")
@is_authenticated
def admin_home():
    logger.debug("admin_home()")
    return render_template("admin/adminhome.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY])


@admin_views_bp.route("/profile")
@is_authenticated
def admin_profile():
    logger.debug("admin_profile()")

    return render_template(
        "admin/profile.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme="https")
