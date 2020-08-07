import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint, url_for, redirect

from utils.okta import OktaAdmin
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config
from utils.email import Email

logger = logging.getLogger(__name__)

# set blueprint
gbac_registration_bp = Blueprint('gbac_registration_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Registration Page
@gbac_registration_bp.route("/registration")
@apply_remote_config
def registration_bp():
    logger.debug("Registration")
    return render_template(
        "/registration.html",
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@gbac_registration_bp.route("/registration-state/<stateToken>", methods=["GET"])
@apply_remote_config
def gbac_registration_state_get(stateToken):
    logger.debug("gbac_registration_state_get()")
    user_id = stateToken
    return render_template(
        "/registration-state.html",
        templatename=get_app_vertical(),
        userid=user_id,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@gbac_registration_bp.route("/registration-state/<user_id>", methods=["POST"])
@apply_remote_config
def gbac_registration_state_post(user_id):
    logger.debug("gbac_registration_state_post()")
    logger.debug(request.form.get('password'))
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_data = okta_admin.get_user(user_id)

    if "errorCode" in user_data:
        logger.error("user_data: {0}".format(user_data))
        return render_template(
            "/registration-state.html",
            userid=user_id,
            templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY],
            error=user_data['errorSummary'])

    user_data["credentials"] = {
        "password": {"value": request.form.get('password')},
        "recovery_question": {
            "question": "Company Name, its Okta.",
            "answer": "Okta"
        }
    }

    logger.debug(user_data)
    user_update_response = okta_admin.update_user(user_id=user_data["id"], user=user_data)

    logger.debug(user_update_response)

    if "errorCode" in user_update_response:
        return render_template(
            "/registration-state.html",
            userid=user_data["id"],
            templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY],
            error=user_update_response['errorCauses'][0]['errorSummary'])

    nresponse = okta_admin.activate_user(user_data["id"], send_email=False)
    logger.debug(nresponse)

    app_already_exists = False
    user_apps = okta_admin.get_applications_by_user_id(user_data["id"])
    for each_app in user_apps:
        if each_app["id"] == session[SESSION_INSTANCE_SETTINGS_KEY]["client_id"]:
            app_already_exists = True

    if not app_already_exists:
        okta_admin.assign_user_to_application(user_data["id"], user_data["profile"]["email"], session[SESSION_INSTANCE_SETTINGS_KEY]["client_id"])

    message = "Registration Complete! Please Login Now!"

    return redirect(url_for("gbac_bp.gbac_login", _external="True", _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"], message=message))


@gbac_registration_bp.route("/registration-completion", methods=["POST"])
@apply_remote_config
def gbac_registration_completion():
    logger.debug("gbac_registration_completion()")

    user_data = {
        "profile": {
            "firstName": request.form.get('firstname'),
            "lastName": request.form.get('lastname'),
            "email": request.form.get('email'),
            "login": request.form.get('email'),
            "primaryPhone": request.form.get('phone'),
            "mobilePhone": request.form.get('phone')
        }
    }
    logger.debug(user_data)
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_create_response = okta_admin.create_user(user=user_data, activate_user='false')
    logger.debug(user_create_response)

    if "id" not in user_create_response:
        error_message = "Failed to get a valid response from Okta Create User: user_data:{0} user_create_response:{1}".format(user_data, user_create_response)
        logger.error(error_message)

        return render_template(
            "/error.html",
            templatename=get_app_vertical(),
            config=session[SESSION_INSTANCE_SETTINGS_KEY],
            error_message=error_message)

    activation_link = ""
    if request.form.get('noemail').lower() == 'true':
        logger.debug("no email will be sent")
        activation_link = url_for(
            "gbac_registration_bp.gbac_registration_state_get",
            stateToken=user_create_response["id"],
            _external=True,
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])
    else:
        logger.debug("email sent")
        emailRegistration(
            recipient={"address": request.form.get('email')},
            token=user_create_response["id"])

    return render_template(
        "/registration-completion.html",
        email=request.form.get('email'),
        activationlink=activation_link,
        noemail=request.form.get('noemail').lower(),
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


# EMail user and admin when a new user registers successfully
def emailRegistration(recipient, token):
    logger.debug("emailRegistration()")
    app_title = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_name"]
    activation_link = url_for(
        "gbac_registration_bp.gbac_registration_state_get",
        stateToken=token,
        _external=True,
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])
    subject = "Welcome to the {app_title}".format(app_title=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_name"])

    message = """
        Thank you for Applying for {app_title}! <br /> <br />Click this link to activate your account. <br /><br />
        <a href='{activation_link}'>Click Here to Activate Account</a>
        """.format(app_title=app_title, activation_link=activation_link)
    test = Email.send_mail(subject=subject, message=message, recipients=[recipient])
    logger.debug(test)
