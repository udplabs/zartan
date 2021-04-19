import logging

from flask import render_template, session, request
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from utils.okta import TokenUtil

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
