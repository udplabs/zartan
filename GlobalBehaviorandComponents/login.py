import os
import base64
import json
import requests
import uuid

#import functions
from functools import wraps
from config import default_settings
from flask import render_template, url_for, redirect, session,request
from flask import send_from_directory, make_response
from flask import Blueprint,g
from flask import Flask, current_app as app
from utils.okta import OktaAuth, OktaAdmin, TokenUtil

#set blueprint
gbac_bp = Blueprint('gbac_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#reference oidc 
from app import oidc, templatename

#main route
@gbac_bp.route("/")
@gbac_bp.route("/index")
def gbac_main():
    user_info = get_user_info() 
    destination = default_settings["settings"]["app_base_url"] + "/" + templatename + "/profile"
    try:
        state = {
            'csrf_token': session['oidc_csrf_token'],
            'destination': oidc.extra_data_serializer.dumps(destination).decode('utf-8')
        }
    except:
        state = ''
        print('No Session')
        
    return render_template(templatename+"/index.html", templatename=templatename, oidc=oidc, user_info=user_info, config=default_settings,state=base64.b64encode(bytes(json.dumps(state),'utf-8')).decode('utf-8')) 


@gbac_bp.route("/login")
def gbac_login():
    #fix: Need to check URL issue for double slash
    destination = default_settings["settings"]["app_base_url"] + "/" + templatename + "/profile" 
    state = {
        'csrf_token': session['oidc_csrf_token'],
        'destination': oidc.extra_data_serializer.dumps(destination).decode('utf-8')
    }
    return render_template("/login.html", templatename=templatename, config=default_settings, oidc=oidc, state=base64.b64encode(bytes(json.dumps(state),'utf-8')).decode('utf-8'))

@gbac_bp.route("/signup")
def gbac_signup():
    return render_template("/signup.html", templatename=templatename, config=default_settings, oidc=oidc)


@gbac_bp.route("/logout")
def gbac_logout():
    oidc.logout()
    return redirect(url_for("gbac_bp.gbac_main", _external="True", _scheme="https"))
    
@gbac_bp.route('/styles')
def gbac_style():
    return render_template("styles/styles.css", config=default_settings),  200, {'Content-Type': 'text/css'}

# Get User Information from OIDC
def get_user_info():
    user_info = None
    try:
        user_info = oidc.user_getinfo(["sub", "name", "email", "locale"])
    except:
        print("User is not authenticated")

    return user_info 
    


"""
routes for MFA verification
"""

@gbac_bp.route("/send_push", methods=["POST"])
def gbac_send_push():
    print("send_push()")
    okta_auth = OktaAuth(default_settings)

    body = request.get_json()
    factor_id = body["factor_id"]
    state_token = body["state_token"]

    response = okta_auth.send_push(factor_id, state_token)
    return json.dumps(response)

@gbac_bp.route("/poll_for_push_verification", methods=["POST"])
def gbac_poll_for_push_verification():
    print("poll_for_push_verification()")
    okta_auth = OktaAuth(default_settings)

    body = request.get_json()
    factor_id = body["factor_id"]
    state_token = body["state_token"]

    response = okta_auth.send_push(factor_id, state_token)
    return json.dumps(response)


@gbac_bp.route("/send_otp_admin", methods=["POST"])
def gbac_send_push_admin():
    print("send_otp_admin()")
    okta_auth = OktaAuth(default_settings)

    body = request.get_json()
    print(body)
    factor_id = body["factor_id"]
    user_id = body["user_id"]
    okta_admin = OktaAdmin(session)


    response = okta_admin.send_otp_admin(factor_id, user_id)
    
    return json.dumps(response)
    
    
@gbac_bp.route("/verify_answer_admin", methods=["POST"])
def gbac_verify_answer_admin():
    print("verify_answer_admin()")
    okta_auth = OktaAuth(default_settings)

    body = request.get_json()
    factor_id = body["factor_id"]
    okta_admin = OktaAdmin(default_settings)
    user_id = body["user_id"]
    pass_code = body["pass_code"]
    response = okta_admin.verify_totp_admin(factor_id, user_id, pass_code)
    print(response)
    return json.dumps(response)


    
@gbac_bp.route("/resend_push", methods=["POST"])
def gbac_resend_push():
    print("resend_push()")

    body = request.get_json()
    factor_id = body["factor_id"]

    if "state_token" in body:
        okta_auth = OktaAuth(default_settings)
        state_token = body["state_token"]
        response = okta_auth.resend_push(factor_id, state_token)
    else:
        okta_admin = OktaAdmin(default_settings)
        user_id = body["user_id"]
        response = okta_admin.resend_push(user_id, factor_id)

    return json.dumps(response)

@gbac_bp.route("/verify_answer", methods=["POST"])
def gbac_verify_answer():
    print("verify_answer()")
    okta_auth = OktaAuth(default_settings)

    body = request.get_json()
    factor_id = body["factor_id"]
    state_token = body["state_token"]
    answer = body["answer"]

    response = okta_auth.verify_answer(factor_id, state_token, answer)
    
    return json.dumps(response)

@gbac_bp.route("/get_authorize_url", methods=["POST"])
def gbac_get_authorize_url():
    print("get_authorize_url()")
    okta_auth = OktaAuth(default_settings)

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
    print("verify_totp()")
    print(session);
    okta_auth = OktaAuth(default_settings)
    
    body = request.get_json()
    pass_code = None
    factor_id = body["factor_id"]
    state_token = body["state_token"]
    # get state with token
    
    if "pass_code" in body:
        pass_code = body["pass_code"]

    print("verifying factor ID {0} with code {1} ({2})".format(factor_id, pass_code, state_token))
    response = okta_auth.verify_totp(factor_id, state_token, pass_code)
    
    
    print(response)
    return json.dumps(response)
    
    
def get_oauth_authorize_url(okta_session_token=None):
    print("get_oauth_authorize_url()")
    okta_auth = OktaAuth(default_settings)

    auth_options = {
        "response_mode": "query",
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

"""
end MFA verification routes
"""
