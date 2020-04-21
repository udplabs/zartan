import os
import base64
import json
import requests
import logging

#import functions
from functools import wraps
from flask import render_template, url_for, redirect, session,request
from flask import send_from_directory, make_response
from flask import Blueprint,g
from flask import Flask, current_app as app
from utils.okta import OktaAuth, OktaAdmin, TokenUtil
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

#set blueprint
streamingservice_views_bp = Blueprint('streamingservice_views_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#Required for Login Landing Page
@streamingservice_views_bp.route("/profile")
@is_authenticated
def streamingservice_profile():
    logger.debug("streamingservice_profile()")
    return render_template("streamingservice/profile.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY])
