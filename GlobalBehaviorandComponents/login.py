import json
import uuid
import logging

# import functions
from flask import render_template, url_for, redirect, session, request
from flask import make_response
from flask import Blueprint
from utils.okta import OktaAuth, OktaAdmin, TokenUtil
from utils.udp import apply_remote_config, clear_session_setting, SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical

from GlobalBehaviorandComponents.validation import get_userinfo, check_okta_api_token, check_zartan_config

logger = logging.getLogger(__name__)

# set blueprint
gbac_bp = Blueprint('gbac_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')

# main route
@gbac_bp.route("/")
@gbac_bp.route("/index")
@apply_remote_config
@check_okta_api_token
@check_zartan_config
def gbac_main():
    logger.debug("gbac_main()")
    return render_template(
        "{0}/index.html".format(get_app_vertical()),
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY], state=str(uuid.uuid4()))


@gbac_bp.route("/clear_session")
def clear_session():
    logger.debug("clear_session()")
    clear_session_setting()
    return redirect(url_for("gbac_bp.gbac_main", _external="True", _scheme="https"))


@gbac_bp.route("/login")
def gbac_login():
    logger.debug("gbac_login()")
    return render_template("/login.html", templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY], state=str(uuid.uuid4()))


@gbac_bp.route("/signup")
def gbac_signup():
    logger.debug("gbac_signup()")
    return render_template("/signup.html", templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY])


@gbac_bp.route("/logout")
def gbac_logout():
    logger.debug("gbac_logout()")
    redirect_url = "{host}/login/signout?fromURI={redirect_path}".format(
        host=session[SESSION_INSTANCE_SETTINGS_KEY]["okta_org_name"],
        redirect_path=url_for("gbac_bp.gbac_main", _external="True", _scheme="https"))

    response = make_response(redirect(redirect_url))
    response.set_cookie(TokenUtil.OKTA_TOKEN_COOKIE_KEY, "")
    return response


@gbac_bp.route('/styles')
def gbac_style():
    return render_template("styles/styles.css", config=session[SESSION_INSTANCE_SETTINGS_KEY]), 200, {'Content-Type': 'text/css'}


"""
routes for MFA verification
"""


@gbac_bp.route("/send_push", methods=["POST"])
def gbac_send_push():
    logger.debug("gbac_send_push()")
    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    body = request.get_json()
    factor_id = body["factor_id"]
    state_token = body["state_token"]

    response = okta_auth.send_push(factor_id, state_token)
    return json.dumps(response)


@gbac_bp.route("/poll_for_push_verification", methods=["POST"])
def gbac_poll_for_push_verification():
    logger.debug("gbac_poll_for_push_verification()")
    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    body = request.get_json()
    factor_id = body["factor_id"]
    state_token = body["state_token"]

    response = okta_auth.send_push(factor_id, state_token)
    return json.dumps(response)


@gbac_bp.route("/send_otp_admin", methods=["POST"])
def gbac_send_push_admin():
    logger.debug("gbac_send_push_admin()")
    body = request.get_json()
    factor_id = body["factor_id"]
    user_id = body["user_id"]
    okta_admin = OktaAdmin(session)

    response = okta_admin.send_otp_admin(factor_id, user_id)

    return json.dumps(response)


@gbac_bp.route("/verify_answer_admin", methods=["POST"])
def gbac_verify_answer_admin():
    logger.debug("gbac_verify_answer_admin()")

    body = request.get_json()
    factor_id = body["factor_id"]
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = body["user_id"]
    pass_code = body["pass_code"]
    response = okta_admin.verify_totp_admin(factor_id, user_id, pass_code)

    return json.dumps(response)


@gbac_bp.route("/resend_push", methods=["POST"])
def gbac_resend_push():
    logger.debug("gbac_resend_push()")

    body = request.get_json()
    factor_id = body["factor_id"]

    if "state_token" in body:
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        state_token = body["state_token"]
        response = okta_auth.resend_push(factor_id, state_token)
    else:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        user_id = body["user_id"]
        response = okta_admin.resend_push(user_id, factor_id)

    return json.dumps(response)


@gbac_bp.route("/verify_answer", methods=["POST"])
def gbac_verify_answer():
    logger.debug("gbac_verify_answer()")

    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    body = request.get_json()
    factor_id = body["factor_id"]
    state_token = body["state_token"]
    answer = body["answer"]

    response = okta_auth.verify_answer(factor_id, state_token, answer)

    return json.dumps(response)


@gbac_bp.route("/get_authorize_url", methods=["POST"])
def gbac_get_authorize_url():
    logger.debug("gbac_get_authorize_url()")
    body = request.get_json()

    session_token = body["session_token"]
    session["state"] = str(uuid.uuid4())

    oauth_authorize_url = get_oauth_authorize_url(session_token)

    response = {
        "authorize_url": oauth_authorize_url
    }
    return json.dumps(response)


@gbac_bp.route("/verify_totp", methods=["POST"])
def gbac_verify_totp():
    logger.debug("gbac_verify_totp()")

    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    body = request.get_json()
    pass_code = None
    factor_id = body["factor_id"]
    state_token = body["state_token"]
    # get state with token

    if "pass_code" in body:
        pass_code = body["pass_code"]

    logger.debug("verifying factor ID {0} with code {1} ({2})".format(factor_id, pass_code, state_token))
    response = okta_auth.verify_totp(factor_id, state_token, pass_code)
    return json.dumps(response)


def get_oauth_authorize_url(okta_session_token=None):
    logger.debug("get_oauth_authorize_url()")
    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    auth_options = {
        "response_mode": "form_post",
        "prompt": "none",
        "scope": "openid profile email"
    }

    if "state" not in session:
        session["oidc_state"] = str(uuid.uuid4())

    if okta_session_token:
        auth_options["sessionToken"] = okta_session_token

    oauth_authorize_url = okta_auth.create_oauth_authorize_url(
        response_type="code",
        state=session["oidc_state"],
        auth_options=auth_options
    )

    return oauth_authorize_url


"""
end MFA verification routes
"""
