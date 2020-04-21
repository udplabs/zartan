import os
import base64
import json
import requests
import uuid
import logging

#import functions

from flask import render_template, url_for, redirect, session,request
from flask import send_from_directory, make_response
from flask import Blueprint,g
from flask import Flask, current_app as app
from utils.okta import OktaAuth, OktaAdmin, TokenUtil
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical

OKTA_TOKEN_COOKIE_KEY = "okta-token-storage"

logger = logging.getLogger(__name__)

#set blueprint
gbac_userapps_bp = Blueprint('gbac_userapps_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')


@gbac_userapps_bp.route("/userapps")
def gbac_userapps_mfa():
    user_info = get_user_info()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    app_info = okta_admin.get_applications_by_user_id(user["id"])

    return render_template("/userapps.html", templatename=get_app_vertical(), config=session[SESSION_INSTANCE_SETTINGS_KEY], applist=app_info)


# Get User Information from OIDC
def get_user_info():
    logger.debug("get_user_info()")
    user_info = TokenUtil.get_claims_from_token(
        TokenUtil.get_id_token(request.cookies, OKTA_TOKEN_COOKIE_KEY))

    return user_info
