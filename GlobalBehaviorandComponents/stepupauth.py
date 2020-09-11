import logging

# import functions
from flask import render_template, session, request
from flask import Blueprint
from utils.okta import OktaAuth
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config

logger = logging.getLogger(__name__)

# set blueprint
gbac_stepupauth_bp = Blueprint('gbac_stepupauth_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@gbac_stepupauth_bp.route("/mfa", methods=['POST'])
@apply_remote_config
def gbac_stepupauth_mfa():
    logger.debug("gbac_stepupauth_mfa()")
    idtoken = request.form['id_token']
    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
    test_token = okta_auth.introspect_mfa(idtoken, session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_stepup_auth_clientid"])
    return render_template("/mfa.html", templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY], idtoken=idtoken, test_token=test_token)
