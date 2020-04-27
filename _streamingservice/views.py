import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY
from utils.okta import TokenUtil

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
streamingservice_views_bp = Blueprint('streamingservice_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')

# Required for Login Landing Page
@streamingservice_views_bp.route("/profile")
@is_authenticated
def streamingservice_profile():
    logger.debug("streamingservice_profile()")
    return render_template(
        "streamingservice/profile.html",
        user_info=get_userinfo(),
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])
