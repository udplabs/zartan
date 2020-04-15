import os
import json
import sys
import jinja2

from os.path import dirname, join
from functools import wraps
from flask import Flask, Blueprint, g
from flask import Flask, send_from_directory,render_template
from config import default_settings
from flask_oidc import OpenIDConnect
from utils.okta import OktaAuth, OktaAdmin, TokenUtil

##############################################
# Get default settings and generate client_secrets.json
# Also set app config
# DO NOT TOUCH
##############################################

with open('client_secrets.json', 'w') as outfile:
    oidc_config = {
        "web": {
            "auth_uri": "{0}/v1/authorize".format(default_settings["issuer"]),
            "client_id": default_settings["client_id"],
            "client_secret": default_settings["client_secret"],
            "redirect_uris": [
                default_settings["redirect_uri"]
            ],
            "okta_api_token": default_settings["okta_api_token"],
            "issuer": "{0}".format(default_settings["issuer"]),
            "token_uri": "{0}/v1/token".format(default_settings["issuer"]),
            "token_introspection_uri": "{0}/v1/introspect".format(default_settings["issuer"]),
            "userinfo_uri": "{0}/v1/userinfo".format(default_settings["issuer"])
        }
    }

    json.dump(oidc_config, outfile, indent=4, sort_keys=True)

    app_config = {
        'SECRET_KEY': default_settings["app_secret_key"],
        'PREFERRED_URL_SCHEME': 'https',
        'OIDC_CLIENT_SECRETS': 'client_secrets.json',
        'OIDC_DEBUG': True,
        'OIDC_COOKIE_SECURE': True,
        'OIDC_USER_INFO_ENABLED': True,
        'OIDC_INTROSPECTION_AUTH_METHOD': 'bearer',
        'OIDC_SCOPES': ["openid", "profile", "email"],
        'OVERWRITE_REDIRECT_URI': default_settings["redirect_uri"],
        'OIDC_CALLBACK_ROUTE': '/authorization-code/callback'
    }

##############################################
# Setting template to use
##############################################
templatename = default_settings["settings"]["app_template"]


##############################################
# Set App Config
# Set OIDC
# DO NOT TOUCH
##############################################

app = Flask(__name__)
app.config.update(app_config)
oidc = OpenIDConnect(app)

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
    print("before_request")
    
    #print( oidc.get_access_token())
    print( oidc.user_loggedin)
    #print( get_user_info())
    
    if oidc.user_loggedin:
        g.user = get_user_info()
        g.token = oidc.get_access_token()

    else:
        g.user = None

def get_user_info():
    user_info = None
    try:
        user_info = oidc.user_getinfo(["sub", "name", "email", "locale"])
    except:
        print("User is not authenticated")

    return user_info 
    
@app.route('/<path:filename>')
def serve_static_html(filename):
    # serve_static_html() generic route function to serve files in the 'static' folder
    print("serve_static_html('{0}')".format(filename))
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)

if __name__ == '__main__':
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True)