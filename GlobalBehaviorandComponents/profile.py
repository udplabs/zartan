import logging
import uuid

# import functions
from flask import render_template, session, request, redirect
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config
from utils.okta import TokenUtil, OktaAuth

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo, FROM_URI_KEY

logger = logging.getLogger(__name__)

# set blueprint
gbac_profile_bp = Blueprint('gbac_profile_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@gbac_profile_bp.route("/profile")
@apply_remote_config
@is_authenticated
def profile_bp():
    logger.debug("profile_bp_profile()")
    if request.args.get('refreshtoken') == 'true':
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

        auth_options = {
            "response_mode": "form_post",
            "prompt": "none",
            "scope": "openid profile email"
        }

        session["oidc_state"] = str(uuid.uuid4())
        session[FROM_URI_KEY] = request.url.replace("http://", "{0}://".format(session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])) + "profile"

        oauth_authorize_url = okta_auth.create_oauth_authorize_url(
            response_type="code",
            state=session["oidc_state"],
            auth_options=auth_options
        )

        return redirect(oauth_authorize_url)
    else:

        return render_template(
            "/profile.html",
            templatename=get_app_vertical(),
            id_token=TokenUtil.get_id_token(request.cookies),
            access_token=TokenUtil.get_access_token(request.cookies),
            user_info=get_userinfo(),
            config=session[SESSION_INSTANCE_SETTINGS_KEY])
