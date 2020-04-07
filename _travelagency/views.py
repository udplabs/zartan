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

from GlobalBehaviorandComponents import login

#set blueprint
travelagency_views_bp = Blueprint('travelagency_views_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#reference oidc
from app import oidc, templatename

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
            return redirect(url_for("gbac_bp.gbac_login", _external="True", _scheme="https"))
    return decorated_function

#check is token is valid with Okta
def is_token_valid_remote(token):
    print("is_token_valid_remote(token)")
    result = False
    okta_auth = OktaAuth(default_settings)

    instrospect_response = okta_auth.introspect(token=token)
    print("instrospect_response: {0}".format(instrospect_response))

    if "active" in instrospect_response:
        result = instrospect_response["active"]

    return result
    

#Required for Login Landing Page
@travelagency_views_bp.route("/profile")
@is_authenticated
def travelagency_profile():
    print("Profile")
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    print(user_info)
    user = okta_admin.get_user(user_info["sub"])
    return render_template("travelagency/profile.html", oidc=oidc, user_info=user_info, config=default_settings)
    
    
@travelagency_views_bp.route("/manageusers")
@is_authenticated
def travelagency_users():
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)

    token = oidc.get_access_token()
    user_group = travelagency_get_group_by_name("everyone")
    print(user_group)
    group_id = user_group["id"]
    group_user_list = okta_admin.get_user_list_by_group_id(group_id)
    return render_template("travelagency/manageusers.html", user_info=user_info, oidc=oidc, userlist= group_user_list, config=default_settings, user_group=user_group)


def travelagency_get_group_by_name(group_name):
    print("get_group_by_name()")
    user_group = None

    if group_name:
        okta_admin = OktaAdmin(default_settings)
        user_groups = okta_admin.get_groups_by_name(group_name)
        # print("user_groups: {0}".format(user_groups))
        if len(user_groups) > 0:
            # just grab the first one... there should only be one match for now
            print(user_groups)
            user_group = user_groups[0]


    return user_group
    
@travelagency_views_bp.route("/suspenduser")
@is_authenticated
def travelagency_user_suspend():
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    user_id = request.args.get('user_id')
    suspend_user = okta_admin.suspend_user(user_id)
    user_info2 = okta_admin.get_user(user_id)

    if not suspend_user:
        message = "User " + user_info2['profile']['firstName'] + " "+  user_info2['profile']['lastName'] +  " Suspended"
    else:
        message = "Error During Suspension"

    return redirect(url_for("travelagency_views_bp.travelagency_users", _external="True", _scheme="https",message=message))

@travelagency_views_bp.route("/unsuspenduser")
@is_authenticated
def travelagency_user_unsuspend():
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    user_id = request.args.get('user_id')
    unsuspend_user = okta_admin.unsuspend_user(user_id)
    user_info2 = okta_admin.get_user(user_id)

    if not unsuspend_user:
        message = "User " + user_info2['profile']['firstName'] + " "+  user_info2['profile']['lastName'] +  " Un-Suspended"
    else:
        message = "Error During Un-Suspension"

    return redirect(url_for("travelagency_views_bp.travelagency_users", _external="True", _scheme="https",message=message))

@travelagency_views_bp.route("/resetpassword")
@is_authenticated
def travelagency_user_resetpassword():
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    user_id = request.args.get('user_id')
    reset_password = okta_admin.reset_password_for_user(user_id)
    user_info2 = okta_admin.get_user(user_id)

    if not reset_password:
        message = "Password Reset for User " + user_info2['profile']['firstName'] + " "+  user_info2['profile']['lastName']
    else:
        message = "Error During Password Reset"

    return redirect(url_for("travelagency_views_bp.travelagency_users", _external="True", _scheme="https",message=message))
    
    
@travelagency_views_bp.route("/manageusercreateupdate")
@is_authenticated
def travelagency_create_update_page():
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    user_id = request.args.get('user_id')
    user_info2 = okta_admin.get_user(user_id)

    return render_template("travelagency/manageusercreateupdate.html", user_info=user_info, oidc=oidc, user_info2=user_info2, config=default_settings)
  

@travelagency_views_bp.route("/createuserinfo", methods=["POST"])
def travelagency_user_create():
    print("Admin Create User()")

    okta_admin = OktaAdmin(default_settings)
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    login = request.form.get('email')
    mobile_phone = request.form.get('phonenumber')

    #  Group and find a Group
    token = oidc.get_access_token()
    group_name = TokenUtil.get_single_claim_from_token(token,"userGroup")


    user_data = {
                "profile": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "login": login,
                    "mobilePhone": mobile_phone
                }
            }

    user_create_response = okta_admin.create_user(user_data)
    print(user_create_response)
    if user_create_response:
        message = "User " + first_name + " "+  last_name+ " was Created"
    else:
        message = "Error During Create"


    return redirect(url_for("travelagency_views_bp.travelagency_users", _external="True", _scheme="https",message=message))
    
    
@travelagency_views_bp.route("/updateuserinfo", methods=["POST"])
@is_authenticated
def travelagency_user_update():
    user_info = login.get_user_info()
    okta_admin = OktaAdmin(default_settings)
    user_id = request.form.get('user_id')
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    mobile_phone = request.form.get('phonenumber')

    user_data = {
                "profile": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "mobilePhone": mobile_phone
                }
            }
    user_update_response = okta_admin.update_user(user_id,user_data)

    if user_update_response:
        message = "User " + first_name + " "+  last_name+ " was Updated"
    else:
        message = "Error During Update"


    return redirect(url_for("travelagency_views_bp.travelagency_users", _external="True", _scheme="https",user_id=user_id,message=message))