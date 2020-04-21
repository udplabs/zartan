import os
import base64
import json
import requests

#import functions
from functools import wraps
from flask import render_template, url_for, redirect, session,request
from flask import send_from_directory, make_response
from flask import Blueprint,g
from flask import Flask, current_app as app
from utils.okta import OktaAuth, OktaAdmin, TokenUtil
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical

from GlobalBehaviorandComponents import login

#set blueprint
gbac_profile_bp = Blueprint('gbac_profile_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')


#needed for validating authentication
def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        print("authenticated()")
        token = g.token
        print("token: {0}".format(token))
        if is_token_valid_remote(token):
            return f(*args, **kws)
        else:
            print("Access Denied")
            #change to different main
            return redirect(url_for("gbac_bp.gbac_login", _external="True", _scheme="https"))
    return decorated_function

#check is token is valid with Okta
def is_token_valid_remote(token):
    print("is_token_valid_remote(token)")
    result = False
    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    instrospect_response = okta_auth.introspect(token=token)
    print("instrospect_response: {0}".format(instrospect_response))

    if "active" in instrospect_response:
        result = instrospect_response["active"]

    return result


#Required for Login Landing Page
@gbac_profile_bp.route("/profile")
@is_authenticated
def profile_bp():
    print("Profile")
    user_info = login.get_user_info()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    print(user_info)
    user = okta_admin.get_user(user_info["sub"])
    return render_template(get_app_vertical()+"/profile.html", templatename=get_app_vertical(), user_info=user_info, config=session[SESSION_INSTANCE_SETTINGS_KEY])

