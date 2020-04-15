import os
import base64
import json
import requests
import uuid

#import functions

from config import default_settings
from flask import render_template, url_for, redirect, session,request
from flask import send_from_directory, make_response
from flask import Blueprint,g
from flask import Flask, current_app as app
from utils.okta import OktaAuth, OktaAdmin, TokenUtil

#set blueprint
gbac_stepupauth_bp = Blueprint('gbac_stepupauth_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#reference oidc 
from app import oidc, templatename

@gbac_stepupauth_bp.route("/mfa", methods=['POST'])
def gbac_stepupauth_mfa():
    idtoken = request.form['id_token']
    okta_auth = OktaAuth(default_settings)
    test_token = okta_auth.introspect_mfa(idtoken,default_settings["settings"]["APP_STEPUP_AUTH_CLIENTID"])
    print(test_token)
    return render_template("/mfa.html", templatename=templatename, config=default_settings, oidc=oidc, idtoken=idtoken,test_token=test_token)


