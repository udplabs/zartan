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
from utils.email import Email

#set blueprint
dealer_views_bp = Blueprint('dealer_views_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#reference oidc
from app import oidc

#needed for validating authentication
def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        print("authenticated()")
        token = g.token

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


#dealer landing page
@dealer_views_bp.route("/profile")
@is_authenticated
def dealer_profile():
    print("Profile")
    user_info = login.get_user_info()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    print(user_info)
    user = okta_admin.get_user(user_info["sub"])
    return render_template(get_app_vertical()+"/profile.html", templatename=get_app_vertical(), oidc=oidc, user_info=user_info, config=session[SESSION_INSTANCE_SETTINGS_KEY])

@dealer_views_bp.route("/registration", methods=["GET","POST"])
def dealer_registration():

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    setup_options = {
        "type_users" : [],
        "dealerships": [],
        "type_user_selected": request.form.get('role'),
        "dealership_selected": request.form.get('location')
    }

    user_data = {
                "profile": {
                    "firstName": "",
                    "lastName": "",
                    "email": "",
                    "login": "",
                    "mobilePhone": ""
                }
            }
    try:

        #Prepopulate choice for setup
        #Get Group
        group_get_response = okta_admin.get_groups_by_name("DEALER_")
        for i in group_get_response:
            setup_options["type_users"].append({"id":i["id"], "description": i["profile"]["description"]})

        group_get_response = okta_admin.get_groups_by_name("_LOC_")
        for i in group_get_response:
            setup_options["dealerships"].append({"id":i["id"], "description": i["profile"]["description"]})

        #On a GET display the registration page with the defaults
        if request.method == "GET":
            return render_template(get_app_vertical()+"/registration.html", templatename=get_app_vertical(),config=session[SESSION_INSTANCE_SETTINGS_KEY],user_data=user_data,setup_options=setup_options)

        #Prepopulate
        user_data = {
                "profile": {
                    "firstName": request.form.get('firstname'),
                    "lastName": request.form.get('lastname'),
                    "email": request.form.get('email'),
                    "login": request.form.get('email'),
                    "mobilePhone": request.form.get('phonenumber')
                },
                 "credentials": {
                        "password" : { "value": request.form.get('password') }
                },
                "groupIds": []
            }

        if request.method == "POST":

            user_data["groupIds"].append(setup_options["type_user_selected"])
            user_data["groupIds"].append(setup_options["dealership_selected"])


            user_create_response = okta_admin.create_user(user_data,activate_user=False)
            if "errorCode" in user_create_response:
                 return render_template(get_app_vertical()+"/registration.html", templatename=get_app_vertical(),config=session[SESSION_INSTANCE_SETTINGS_KEY], error = user_create_response, user_data=user_data,setup_options=setup_options)

            #Send Activattion Email
            subject = "Welcome to the {app_title}".format(app_title=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_name"])
            message = ("Welcome to the {app_title}! Click this link to activate your account <br />"
                      "<a href='{activation_link}'>{activation_link}</a>").format(
                app_title=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_name"],
                activation_link=url_for( "dealer_views_bp.dealer_registration_state",stateToken = user_create_response["id"],_external=True, _scheme="https"))

            send_email_response = Email.send_mail(subject=subject,message=message,recipients=[{"address": request.form.get('email')}])

    except Exception as e:
        return render_template(get_app_vertical()+"/registration.html", templatename=get_app_vertical(),config=session[SESSION_INSTANCE_SETTINGS_KEY], error = e, user_data=user_data,setup_options=setup_options)

    return render_template(get_app_vertical()+"/registration-completion.html", templatename=get_app_vertical(),config=session[SESSION_INSTANCE_SETTINGS_KEY], email=request.form.get('email'))

@dealer_views_bp.route("/registration-state/<stateToken>", methods=["GET"])
def dealer_registration_state(stateToken):
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = stateToken
    user_activate_response = okta_admin.activate_user(user_id,send_email=False)
    if "errorCode" in user_activate_response:
        return render_template(get_app_vertical()+"/registration-state.html", templatename=get_app_vertical(),config=session[SESSION_INSTANCE_SETTINGS_KEY], error = user_activate_response)

    return render_template(get_app_vertical()+"/registration-state.html", templatename=get_app_vertical(),config=session[SESSION_INSTANCE_SETTINGS_KEY])

@dealer_views_bp.route("/registration-completion", methods=["GET"])
def dealer_registration_completion():
    return render_template(get_app_vertical()+"/registration-completion.html", templatename=get_app_vertical(),config=session[SESSION_INSTANCE_SETTINGS_KEY])