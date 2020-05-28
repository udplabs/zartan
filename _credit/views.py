import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint, redirect, url_for
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from utils.okta import TokenUtil, OktaAdmin
from utils.email import Email

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
        applistall=app_all_info)


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


@credit_views_bp.route("/registration", methods=["GET"])
def credit_registration_get():
    logger.debug("credit_registration_get()")
    return render_template(
        "{0}/registration.html".format(get_app_vertical()),
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        user_info=get_userinfo(),
        _scheme="https")


@credit_views_bp.route("/registration-state/<stateToken>", methods=["GET"])
def credit_registration_state_get(stateToken):
    logger.debug("dealer_registration_state_get()")
    user_id = stateToken
    return render_template(
        "{0}/registration-state.html".format(get_app_vertical()),
        templatename=get_app_vertical(),
        userid=user_id,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme="https")


@credit_views_bp.route("/registration-state/<stateToken>", methods=["POST"])
def credit_registration_state_post(stateToken):
    logger.debug("dealer_registration_state_get()")
    user_id = stateToken
    logger.debug(request.form.get('inputPassword'))
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_data = {
        "credentials": {
            "password": {"value": request.form.get('password')}
        }
    }
    user_update_response = okta_admin.update_user(user_id=user_id, user=user_data)

    logger.debug(user_update_response)

    if "errorCode" in user_update_response:
        return render_template(
            "{0}/registration-state.html".format(get_app_vertical()),
            userid=user_id,
            templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY],
            error=user_update_response['errorCauses'][0]['errorSummary'])

    okta_admin.activate_user(user_id, send_email=False)
    group_info = okta_admin.get_application_groups(session[SESSION_INSTANCE_SETTINGS_KEY]["client_id"])
    group_id = group_info[0]["id"]
    okta_admin.assign_user_to_group(group_id, user_id)
    message = "Registration Complete! Please Login Now!"
    return redirect(url_for("gbac_bp.gbac_login", _external="True", _scheme="https", message=message))


@credit_views_bp.route("/registration-completion", methods=["POST"])
def credit_registration_completion():
    logger.debug("credit_registration_completion()")

    user_data = {
        "profile": {
            "firstName": request.form.get('firstname'),
            "lastName": request.form.get('lastname'),
            "email": request.form.get('email'),
            "login": request.form.get('email'),
        }
    }
    logger.debug(user_data)
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_create_response = okta_admin.create_user(user=user_data, activate_user='false')
    logger.debug(user_create_response)
    emailRegistration(
        recipient={"address": request.form.get('email')},
        token=user_create_response["id"])

    return render_template(
        "{0}/registration-completion.html".format(get_app_vertical()),
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme="https")


# EMail user and admin when a new user registers successfully
def emailRegistration(recipient, token):
    logger.debug("emailRegistration()")
    app_title = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_name"]
    activation_link = url_for("credit_views_bp.credit_registration_state_get", stateToken=token, _external=True, _scheme="https")
    subject = "Welcome to the {app_title}".format(app_title=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_name"])

    message = """
        Thank you for Applying for {app_title}! Click this link to activate your account <br />
        <a href='{activation_link}'>{activation_link}</a>).
        """.format(app_title=app_title, activation_link=activation_link)
    test = Email.send_mail(subject=subject, message=message, recipients=[recipient])
    logger.debug(test)
