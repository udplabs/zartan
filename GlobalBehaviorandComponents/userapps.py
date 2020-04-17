import os
import base64
import json
import requests
import uuid

#import functions

from flask import render_template, url_for, redirect, session,request
from flask import send_from_directory, make_response
from flask import Blueprint,g
from flask import Flask, current_app as app
from utils.okta import OktaAuth, OktaAdmin, TokenUtil
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical

#set blueprint
gbac_userapps_bp = Blueprint('gbac_userapps_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#reference oidc
from app import oidc

@gbac_userapps_bp.route("/userapps")
def gbac_userapps_mfa():
    user_info = get_user_info()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    app_info = okta_admin.get_applications_by_user_id(user["id"])
    
    return render_template("/userapps.html", templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY], oidc=oidc, applist=app_info)


# Get User Information from OIDC
def get_user_info():
    user_info = None
    try:
        user_info = oidc.user_getinfo(["sub", "name", "email", "locale"])
    except:
        print("User is not authenticated")

    return user_info
