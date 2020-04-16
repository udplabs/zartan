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
gbac_stepupauth_bp = Blueprint('gbac_stepupauth_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#reference oidc
from app import oidc

@gbac_stepupauth_bp.route("/mfa", methods=['POST'])
def gbac_stepupauth_mfa():
    idtoken = request.form['id_token']
    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
    test_token = okta_auth.introspect_mfa(idtoken,session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_stepup_auth_clientid"])
    print(test_token)
    return render_template("/mfa.html", templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY], oidc=oidc, idtoken=idtoken,test_token=test_token)


