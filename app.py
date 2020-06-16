import os
import json
import logging
import logging.config

from flask import Flask, send_from_directory, render_template
from flask import request, session, make_response, redirect
from config.app_config import default_settings

from utils.okta import OktaAuth, TokenUtil
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from GlobalBehaviorandComponents.validation import gvalidation_bp_error, FROM_URI_KEY

##############################################
# Get default settings and generate client_secrets.json
# Also set app config
# DO NOT TOUCH
##############################################
logger = logging.getLogger(__name__)

app_config = {
    'SECRET_KEY': default_settings["app_secret_key"],
}

##############################################
# Set App Config
# DO NOT TOUCH
##############################################

app = Flask(__name__)
app.config.update(app_config)

##############################################
# Custom Apps
# Include all routing files
# Add more themes and routes for themese here
##############################################

# home and login
from GlobalBehaviorandComponents.login import gbac_bp
app.register_blueprint(gbac_bp, url_prefix='/')

from GlobalBehaviorandComponents.manageusers import gbac_manageusers_bp
app.register_blueprint(gbac_manageusers_bp, url_prefix='/')

from GlobalBehaviorandComponents.stupupauth import gbac_stepupauth_bp
app.register_blueprint(gbac_stepupauth_bp, url_prefix='/')

from GlobalBehaviorandComponents.userapps import gbac_userapps_bp
app.register_blueprint(gbac_userapps_bp, url_prefix='/')

from GlobalBehaviorandComponents.profile import gbac_profile_bp
app.register_blueprint(gbac_profile_bp, url_prefix='/')

from GlobalBehaviorandComponents.registration import gbac_registration_bp
app.register_blueprint(gbac_registration_bp, url_prefix='/')

from GlobalBehaviorandComponents.validation import gvalidation_bp, get_userinfo
app.register_blueprint(gvalidation_bp, url_prefix='/')

from GlobalBehaviorandComponents.mfaenrollment import gbac_mfaenrollment_bp
app.register_blueprint(gbac_mfaenrollment_bp, url_prefix='/')

# sample theme
from _sample.views import sample_views_bp
app.register_blueprint(sample_views_bp, url_prefix='/sample')

# travel agency theme
from _travelagency.views import travelagency_views_bp
app.register_blueprint(travelagency_views_bp, url_prefix='/travelagency')

# hospitality  theme
from _hospitality.views import hospitality_views_bp
app.register_blueprint(hospitality_views_bp, url_prefix='/hospitality')

# dealer theme
from _dealer.views import dealer_views_bp
app.register_blueprint(dealer_views_bp, url_prefix='/dealer')

# streaming service theme
from _streamingservice.views import streamingservice_views_bp
app.register_blueprint(streamingservice_views_bp, url_prefix='/streamingservice')

# finance theme
from _finance.views import finance_views_bp
app.register_blueprint(finance_views_bp, url_prefix='/finance')

# admin theme
from _admin.views import admin_views_bp
app.register_blueprint(admin_views_bp, url_prefix='/admin')

# credit theme
from _credit.views import credit_views_bp
app.register_blueprint(credit_views_bp, url_prefix='/credit')

# patientportal theme
from _patientportal.views import patientportal_views_bp
app.register_blueprint(patientportal_views_bp, url_prefix='/patientportal')


##############################################
# Main Shared Routes
# DO NOT TOUCH
##############################################

@app.route('/<path:filename>')
def serve_static_html(filename):
    # serve_static_html() generic route function to serve files in the 'static' folder
    logger.debug("serve_static_html('{0}')".format(filename))
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)


@app.route('/healthcheck')
def healthcheck():
    return "OK"


"""
   Set path to '/authorization-code/callback' because of backward compatibility with flask-oidc legacy config
"""


@app.route('/authorization-code/callback', methods=["POST"])
def oidc_callback_handler():
    """ handler for the oidc call back of the app """
    logger.debug("oidc_callback_handler()")
    response = None
    logger.debug(request.form)
    has_app_level_mfa_policy = False

    if "code" in request.form:
        oidc_code = request.form["code"]
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        oauth_token = okta_auth.get_oauth_token(
            code=oidc_code,
            grant_type="authorization_code",
            auth_options={
                "client_id": session[SESSION_INSTANCE_SETTINGS_KEY]["client_id"],
                "client_secret": session[SESSION_INSTANCE_SETTINGS_KEY]["client_secret"],
            }
        )
        logger.debug("oauth_token: {0}".format(json.dumps(oauth_token, indent=4, sort_keys=True)))
        app_landing_page_url = get_post_login_landing_page_url()

        response = make_response(redirect(app_landing_page_url))

        okta_token_cookie = TokenUtil.create_encoded_okta_token_cookie(
            oauth_token["access_token"],
            oauth_token["id_token"])
        # logger.debug("okta_token_cookie: {0}".format(okta_token_cookie))

        response.set_cookie(TokenUtil.OKTA_TOKEN_COOKIE_KEY, okta_token_cookie)
    elif "error" in request.form:
        # This is in the case there is an Okta App level MFA policy
        logger.error("ERROR: {0}, MESSAGE: {1}".format(request.form["error"], request.form["error_description"]))
        if ("The client specified not to prompt, but the client app requires re-authentication or MFA." == request.form["error_description"]):
            has_app_level_mfa_policy = True

        # Error occured with Accessing the app instance
        if has_app_level_mfa_policy:
            error_message = "Failed to Authenticate.  Please remove App Level MFA Policy and use a Global MFA Policy. Error: {0} - {1}".format(
                request.form["error"],
                request.form["error_description"]
            )
            response = gvalidation_bp_error(error_message)
        else:
            error_message = "Failed to Authenticate.  Check to make sure the user has access to the application. Error: {0} - {1}".format(
                request.form["error"],
                request.form["error_description"]
            )

            response = gvalidation_bp_error(error_message)
    else:
        # catch all error
        response = gvalidation_bp_error("Failed to Authenticate.  Check to make sure the user has access to the application.")

    return response


def get_post_login_landing_page_url():
    app_landing_page_url = ""

    # Pull from Confg
    if not session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_base_url"]:
        session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_base_url"] = request.url_root.replace("http:", "https:")
        logger.debug("app_base_url: {0}".format(session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_base_url"]))

    app_landing_page_url = "{app_base_url}/{app_template}/{landing_page}".format(
        app_base_url=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_base_url"],
        app_template=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_template"],
        landing_page=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_post_login_landing_url"],
    )

    # Check for from from_uri... this always overrides the config
    if FROM_URI_KEY in session:
        if session[FROM_URI_KEY]:
            app_landing_page_url = session[FROM_URI_KEY]
            session[FROM_URI_KEY] = ""

    logger.debug("app landing page {0}".format(app_landing_page_url))

    return app_landing_page_url


def page_not_found(e):
    return render_template('404.html', user_info=get_userinfo(), templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY]), 404


app.register_error_handler(404, page_not_found)

if __name__ == '__main__':
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", os.getenv("LOGGER_CONFIG", "DEV_logger.config"))
    logging.config.fileConfig(fname=log_file_path, disable_existing_loggers=False)
    logger.debug("default_settings: {0}".format(json.dumps(default_settings, indent=4, sort_keys=True)))
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True)
