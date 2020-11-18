import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint, url_for, redirect

from utils.okta import OktaAdmin
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config
from utils.email import Email

logger = logging.getLogger(__name__)

# set blueprint
gbac_findusername_bp = Blueprint('gbac_findusername_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Registration Page
@gbac_findusername_bp.route("/findusername")
@apply_remote_config
def findusername_bp():
    logger.debug("findusername")
    return render_template(
        "/findusername.html",
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@gbac_findusername_bp.route("/find-user", methods=["POST"])
@apply_remote_config
def gbac_finduser_completion():
    logger.debug("gbac_finduser_completion()")

    firstName = request.form.get('firstname')
    lastName = request.form.get('lastname')
    primaryPhone = request.form.get('phone')

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_response = ""
    message = ""
    email = ""
    login = ""
    if primaryPhone:
        user_response = okta_admin.get_user_list_by_search("profile.primaryPhone eq \"" + primaryPhone + "\"&limit=1")
    else:
        user_response = okta_admin.get_user_list_by_search("profile.firstName eq \"" + firstName + "\" and profile.lastName eq \"" + lastName + "\"&limit=1")

    if user_response:
        login = user_response[0]['profile']['login']
        recipients = []
        recipients.append({"address": user_response[0]["profile"]["email"]})
        emailLogin(recipients, login)
        message = "Your Username was found. An email is being sent to: " + user_response[0]["profile"]["email"]
    else:
        message = "Your Username was not found. Please try again."

    return redirect(
        url_for(
            "gbac_findusername_bp.findusername_bp",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            email=email,
            message=message))


def emailLogin(recipient, username):
    logger.debug("emailRegistration()")

    subject = "Your Username was Found"

    message = """
        You have requested to retrieve your username. <br /> <br />Your Username is: {username}<br /> <br />
        <br /> <br />If you did not request to retrieve
         your username, please contact us at your earliest convenience.
        """.format(username=username)

    test = Email.send_mail(subject=subject, message=message, recipients=recipient)
    logger.debug(test)
