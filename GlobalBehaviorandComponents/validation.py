import logging

from functools import wraps

from flask import redirect, request, url_for, session, Blueprint, render_template

from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from utils.okta import TokenUtil

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
            # change to different main
            return redirect(url_for("gbac_bp.gbac_login", _external="True", _scheme="https"))
    return decorated_function


# Get User Information from OIDC
def get_userinfo():
    logger.debug("get_userinfo()")

    user_info = TokenUtil.get_claims_from_token(
        TokenUtil.get_id_token(request.cookies))

    return user_info


@gvalidation_bp.route("/error")
def gvalidation_bp_error(error_message=""):
    logger.debug("gvalidation_bp_error()")

    return render_template(
        "/error.html",
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        error_message=error_message)
