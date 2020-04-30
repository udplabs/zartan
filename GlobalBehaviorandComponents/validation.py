import logging
import uuid

from functools import wraps

from flask import redirect, request, url_for, session, Blueprint, render_template, Markup

from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, is_apitoken_valid, is_config_valid
from utils.udp import SESSION_IS_APITOKEN_VALID_KEY, SESSION_IS_CONFIG_VALID_KEY
from utils.okta import TokenUtil, OktaAdmin, OktaAuth


FROM_URI_KEY = "from_uri"
GET_NEW_TOKEN_URL = "get_new_token_url"
logger = logging.getLogger(__name__)

gvalidation_bp = Blueprint('gvalidation_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        logger.debug("authenticated()")

        token = TokenUtil.get_access_token(request.cookies)
        # logger.debug("token: {0}".format(token))

        if TokenUtil.is_valid_remote(token, session[SESSION_INSTANCE_SETTINGS_KEY]):
            return f(*args, **kws)
        else:
            logger.debug("Access Denied")
            session[FROM_URI_KEY] = request.url
            # change to different main
            return redirect(url_for("gbac_bp.gbac_login", _external="True", _scheme="https"))
    return decorated_function


def check_okta_api_token(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        logger.debug("check_okta_api_token()")
        response = None

        if not is_apitoken_valid():
            okta_api_token = session[SESSION_INSTANCE_SETTINGS_KEY]["okta_api_token"]
            logger.debug("okta_api_token: {0}".format(okta_api_token))

            if okta_api_token:
                okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
                groups = okta_admin.get_groups_by_name("Everyone")
                if "errorSummary" in groups:
                    if "Invalid token provided" == groups["errorSummary"]:
                        response = gvalidation_bp_error("Okta API Token is invalid!")
                else:
                    session[SESSION_IS_APITOKEN_VALID_KEY] = True
            else:
                response = gvalidation_bp_error("Okta API Token is not set!")

            if response:
                return response

        return f(*args, **kws)

    return decorated_function


def check_zartan_config(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        logger.debug("check_zartan_config()")

        if not is_config_valid():
            error_message_list = ["The following configuration issue were found:<br /><ul>"]

            zartan_config = session[SESSION_INSTANCE_SETTINGS_KEY]
            # logger.debug("zartan_config: {0}".format(zartan_config))

            if zartan_config:
                check_if_set_in_config(zartan_config, error_message_list)

                if "settings" in zartan_config:
                    if "app_template" in zartan_config["settings"]:
                        if not zartan_config["settings"]["app_template"]:
                            error_message_list.append("'app_template' is not set in the config.<br />")

            else:
                error_message_list.append("Zartan Config is not set!")

            error_message_list.append("</ul>Please correct the issues and clear the app session to try again")
            error_message = "".join(error_message_list)

            if len(error_message_list) > 2:  # the first two items are just prep text for the errors any more are actuall errors
                return gvalidation_bp_error(error_message)
            else:
                session[SESSION_IS_CONFIG_VALID_KEY] = True

        return f(*args, **kws)

    return decorated_function


def check_if_set_in_config(config_settings, error_message_list):
    logger.debug("check_if_set_in_config()")

    for key, value in config_settings.items():
        if key in config_settings:
            if not value:
                error_message_list.append("<li>'{attribute}' is not set in the config.</li>".format(attribute=key))
        else:
            error_message_list.append("<li>'{attribute}' is not set in the config.</li>".format(attribute=key))


# Get User Information from OIDC
def get_userinfo():
    logger.debug("get_userinfo()")
    user_info = None
    session[SESSION_INSTANCE_SETTINGS_KEY][GET_NEW_TOKEN_URL] = ""

    if TokenUtil.is_valid_remote(TokenUtil.get_access_token(request.cookies), session[SESSION_INSTANCE_SETTINGS_KEY]):
        logger.debug("valid")
        user_info = TokenUtil.get_claims_from_token(
            TokenUtil.get_id_token(request.cookies))
    else:
        logger.debug("notvalid")
        session[SESSION_INSTANCE_SETTINGS_KEY][GET_NEW_TOKEN_URL] = get_oauth_authorize_url()
    return user_info


@gvalidation_bp.route("/error")
def gvalidation_bp_error(error_message=""):
    logger.debug("gvalidation_bp_error()")

    return render_template(
        "/error.html",
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        error_message=Markup(error_message))


def get_oauth_authorize_url(okta_session_token=None):
    logger.debug("get_oauth_authorize_url()")
    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    auth_options = {
        "response_mode": "form_post",
        "prompt": "none",
        "scope": "openid profile email"
    }

    if "state" not in session:
        session["state"] = str(uuid.uuid4())

    if okta_session_token:
        auth_options["sessionToken"] = okta_session_token

    oauth_authorize_url = okta_auth.create_oauth_authorize_url(
        response_type="code",
        state=session["state"],
        auth_options=auth_options
    )

    return oauth_authorize_url
