import os
import base64
import json
import requests

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
    state = {
        'csrf_token': session['oidc_csrf_token'],
        'destination': oidc.extra_data_serializer.dumps(destination).decode('utf-8')
    }
    return render_template(templatename+"/index.html", templatename=templatename, oidc=oidc, user_info=user_info, config=default_settings,state=base64.b64encode(bytes(json.dumps(state),'utf-8')).decode('utf-8')) 


@gbac_bp.route("/login")
def gbac_login():
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
    return redirect("index")
    
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
    



