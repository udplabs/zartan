import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint, redirect
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from utils.okta import TokenUtil, OktaAdmin

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
    return render_template("credit/account.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY], _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@credit_views_bp.route("/mycredit")
@is_authenticated
def credit_mycredit():
    logger.debug("credit_mycredit()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    app_all_info = okta_admin.get_applications_all()
    app_info = okta_admin.get_applications_by_user_id(user["id"])

    return render_template(
        "credit/mycredit.html",
        user_info=get_userinfo(),
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        applist=app_info,
        applistall=app_all_info, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@credit_views_bp.route("/getmorecredit/<app_id>")
@is_authenticated
def credit_getmorecredit(app_id):
    logger.debug("credit_getmorecredit()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    app_info = okta_admin.get_applications_by_id(app_id)
    group_info = okta_admin.get_application_groups(app_id)
    group_id = group_info[0]["id"]
    user_id = user["id"]
    okta_admin.assign_user_to_group(group_id, user_id)
    app_url = app_info["settings"]["oauthClient"]["initiate_login_uri"]

    return redirect(app_url)
