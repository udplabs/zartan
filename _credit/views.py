import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY
from utils.okta import TokenUtil

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
credit_views_bp = Blueprint('credit_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@credit_views_bp.route("/profile")
@is_authenticated
def credit_profile():
    logger.debug("credit_profile()")
    return render_template(
        "credit/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


# Account Page
@credit_views_bp.route("/account")
@is_authenticated
def credit_account():
    logger.debug("credit_account()")
    return render_template("credit/account.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY])
