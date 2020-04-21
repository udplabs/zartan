import logging

from functools import wraps

from flask import redirect, request, url_for, session

from utils.udp import SESSION_INSTANCE_SETTINGS_KEY
from utils.okta import TokenUtil

logger = logging.getLogger(__name__)


def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        logger.debug("authenticated()")
        token = TokenUtil.get_access_token(request.cookies)
        logger.debug("token: {0}".format(token))

        if TokenUtil.is_valid_remote(token, session[SESSION_INSTANCE_SETTINGS_KEY]):
            return f(*args, **kws)
        else:
            logger.debug("Access Denied")
            #change to different main
            return redirect(url_for("gbac_bp.gbac_login", _external="True", _scheme="https"))
    return decorated_function


# Get User Information from OIDC
def get_userinfo():
    logger.debug("get_userinfo()")
    user_info = TokenUtil.get_claims_from_token(
        TokenUtil.get_id_token(request.cookies))

    return user_info