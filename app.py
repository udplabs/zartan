import os
import json
import sys
import jinja2
import logging
import logging.config

from os.path import dirname, join

from functools import wraps
from flask import Flask, Blueprint, g
from flask import Flask, send_from_directory, render_template
from flask import request, session, make_response, redirect, url_for
from config import default_settings

from utils.okta import OktaAuth, OktaAdmin, TokenUtil
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY

##############################################
# Get default settings and generate client_secrets.json
# Also set app config
# DO NOT TOUCH
##############################################
logger = logging.getLogger(__name__)

app_config = {
    'SECRET_KEY': default_settings["app_secret_key"],
}

OKTA_TOKEN_COOKIE_KEY = "okta-token-storage"

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

#home and login
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

#sample theme
from _sample.views import sample_views_bp
app.register_blueprint(sample_views_bp, url_prefix='/sample')

#travel agency theme
from _travelagency.views import travelagency_views_bp
app.register_blueprint(travelagency_views_bp, url_prefix='/travelagency')

#hospitality  theme
from _hospitality.views import hospitality_views_bp
app.register_blueprint(hospitality_views_bp, url_prefix='/hospitality')


#dealer theme
from _dealer.views import dealer_views_bp
app.register_blueprint(dealer_views_bp, url_prefix='/dealer')


#streaming service theme
from _streamingservice.views import streamingservice_views_bp
app.register_blueprint(streamingservice_views_bp, url_prefix='/streamingservice')

#finance theme
from _finance.views import finance_views_bp
app.register_blueprint(finance_views_bp, url_prefix='/finance')


##############################################
# Main Shared Routes
# DO NOT TOUCH
##############################################

@app.before_request
def before_request():
    # logger.debug("before_request()")
    access_token = TokenUtil.get_access_token(request.cookies, OKTA_TOKEN_COOKIE_KEY)
    logger.debug("access_token: {0}".format(access_token))
    if access_token:
            g.user = get_user_info()
            g.token = access_token
    else:
        g.user = None
        g.token = None

def get_user_info():
    logger.debug("get_user_info()")
    user_info = TokenUtil.get_claims_from_token(
        TokenUtil.get_id_token(request.cookies, OKTA_TOKEN_COOKIE_KEY))

    return user_info


@app.route('/<path:filename>')
def serve_static_html(filename):
    # serve_static_html() generic route function to serve files in the 'static' folder
    print("serve_static_html('{0}')".format(filename))
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)


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

    # This is in the case there is an Okta App level MFA policy
    if "error" in request.form:
        logger.error("ERROR: {0}, MESSAGE: {1}".format(request.form["error"], request.form["error_description"]))
        if ("The client specified not to prompt, but the client app requires re-authentication or MFA." == request.form["error_description"]):
            has_app_level_mfa_policy = True

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
        app_landing_page_url = url_for("gbac_bp.gbac_main", _external="True", _scheme="https")
        logger.debug("app landing page {0}".format(app_landing_page_url))

        response = make_response(redirect(app_landing_page_url))

        okta_token_cookie = TokenUtil.create_encoded_okta_token_cookie(
            oauth_token["access_token"],
            oauth_token["id_token"])

        logger.debug("okta_token_cookie: {0}".format(okta_token_cookie))

        response.set_cookie(OKTA_TOKEN_COOKIE_KEY, okta_token_cookie)
    elif "error" in request.form:
        # Error occured with Accessing the app instance
        if has_app_level_mfa_policy:
            response = make_response(
                render_template(
                    "error.html",
                    config=session[SESSION_INSTANCE_SETTINGS_KEY],
                    error_message="Failed to Authenticate.  Please remove App Level MFA Policy and use a Global MFA Policy. Error: {0} - {1}".format(
                        request.form["error"],
                        request.form["error_description"]
                        )
                )
            )
        else:
            response = make_response(
                render_template(
                    "error.html",
                    config=session[SESSION_INSTANCE_SETTINGS_KEY],
                    error_message="Failed to Authenticate.  Check to make sure the user has patient access to the application. Error: {0} - {1}".format(
                        request.form["error"],
                        request.form["error_description"]
                        )
                )
            )
    else:
        # catch all error
        response = make_response(
            render_template(
                "error.html",
                config=session[SESSION_INSTANCE_SETTINGS_KEY],
                error_message="Failed to Authenticate.  Check to make sure the user has access to the application."
            )
        )

    return response


if __name__ == '__main__':
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv("LOGGER_CONFIG", "DEV_logger.config"))
    logging.config.fileConfig(fname=log_file_path, disable_existing_loggers=False)

    logger.debug("default_settings: {0}".format(json.dumps(default_settings, indent=4, sort_keys=True)))
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True)