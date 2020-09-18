import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, apply_remote_config
from utils.okta import TokenUtil

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
finance_views_bp = Blueprint('finance_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@finance_views_bp.route("/profile")
@apply_remote_config
@is_authenticated
def finance_profile():
    logger.debug("finance_profile()")
    return render_template(
        "finance/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


# Account Page
@finance_views_bp.route("/account")
@apply_remote_config
@is_authenticated
def finance_account():
    logger.debug("finance_account()")
    return render_template("finance/account.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY])
