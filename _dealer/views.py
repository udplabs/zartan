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
from app import oidc, templatename

from GlobalBehaviorandComponents import login
from utils.email import Email


#set blueprint
dealer_views_bp = Blueprint('dealer_views_bp', __name__,template_folder='templates', static_folder='static', static_url_path='static')

#reference oidc
from app import oidc, templatename

#needed for validating authentication
def is_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if hasattr(g, 'token'):
            token = g.token
            if is_token_valid_remote(token):
                return f(*args, **kws)
        #change to different main
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

#dealer landing page
@dealer_views_bp.route("/profile")
@is_authenticated
def dealer_profile():
    print("Profile")
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    print(user_info)
    user = okta_admin.get_user(user_info["sub"])
    print(user)
    return render_template(templatename+"/profile.html", templatename=templatename, oidc=oidc, user_info=user_info, config=default_settings, _scheme="https")

@dealer_views_bp.route("/registration", methods=["GET","POST"])
def dealer_registration():
    
    okta_admin = OktaAdmin(default_settings)
    
    send_email_response_admin = emailAllMembersOfGroup(group_id="00g3jy1jatm7h3CI7357", subject="ADMIN", message="TEST")
    
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
        group_get_response = okta_admin.get_groups_by_name("DEALER_ADMIN")
        for i in group_get_response:
            setup_options["type_users"].append({"id":i["id"], "description": i["profile"]["description"]})
            group_id_dealer_admin = i["id"]
            
        group_get_response = okta_admin.get_groups_by_name("DEALER_USER")
        for i in group_get_response:
            setup_options["type_users"].append({"id":i["id"], "description": i["profile"]["description"]})    
            
        group_get_response = okta_admin.get_groups_by_name("_LOC_")
        for i in group_get_response: 
            setup_options["dealerships"].append({"id":i["id"], "description": i["profile"]["description"]})
            group_id_location = i["id"]
        
        #On a GET display the registration page with the defaults    
        if request.method == "GET":
            return render_template(templatename+"/registration.html", templatename=templatename,config=default_settings,user_data=user_data,setup_options=setup_options, _scheme="https")
        
        #Prepopulate    
        user_data = {
                "profile": {
                    "firstName": request.form.get('firstname'),
                    "lastName": request.form.get('lastname'),
                    "email": request.form.get('email'),
                    "login": request.form.get('email'),
                    "mobilePhone": request.form.get('phonenumber'),
                    "organization": request.form.get('location')
                },
                 "credentials": {
                        "password" : { "value": request.form.get('password') }
                },
                "groupIds": []
            }
            
        if request.method == "POST":
            user_data["groupIds"].append(setup_options["type_user_selected"])
            #user_data["groupIds"].append(setup_options["dealership_selected"])
            
            user_create_response = okta_admin.create_user(user_data,activate_user=False)
            if "errorCode" in user_create_response:
                 return render_template(templatename+"/registration.html", templatename=templatename,config=default_settings, error = user_create_response, user_data=user_data,setup_options=setup_options) 
            
            #Send Activation Email to the user
            subject = "Welcome to the {app_title}".format(app_title=default_settings["settings"]["app_name"])
            message = ("Welcome to the {app_title}! Click this link to activate your account <br />"
                      "<a href='{activation_link}'>{activation_link}</a>").format(
                app_title=default_settings["settings"]["app_name"],
                activation_link=url_for( "dealer_views_bp.dealer_registration_state",stateToken = user_create_response["id"],_external=True, _scheme="https"))
            send_email_response = Email.send_mail(subject=subject,message=message,recipients=[{"address": request.form.get('email')}])
            
            #Send Activation Email to the Admin
            subject_admin = "Registration Activation request for user {user}".format(user = request.form.get('email'))
            message_admin = ("A new user has registered. His request is awaiting your approval. Click this link to log into your account <br />"
                      "<a href='{activation_link}'>{activation_link}</a> to review the request").format(
                activation_link=url_for( "dealer_views_bp.workflow_approvals",_external=True, _scheme="https"))
            send_email_response_admin = emailAllMembersOfGroup(group_id="00g3jy1jatm7h3CI7357", subject=subject_admin, message=message_admin)
            
    except Exception as e:
        return render_template(templatename+"/registration.html", templatename=templatename,config=default_settings, error = e, user_data=user_data,setup_options=setup_options, _scheme="https") 
        
    return render_template(templatename+"/registration-completion.html", templatename=templatename,config=default_settings, email=request.form.get('email'), _scheme="https")

@dealer_views_bp.route("/registration-state/<stateToken>", methods=["GET"])
def dealer_registration_state(stateToken):
    user_id = stateToken
    okta_admin = OktaAdmin(default_settings)
    user_activate_response = okta_admin.activate_user(user_id,send_email=False)
    if "errorCode" in user_activate_response:
        return render_template(templatename+"/registration-state.html", templatename=templatename,config=default_settings, error = user_activate_response) 
            
    return render_template(templatename+"/registration-state.html", templatename=templatename,config=default_settings, _scheme="https")
    
@dealer_views_bp.route("/registration-completion", methods=["GET"])
def dealer_registration_completion():
    return render_template(templatename+"/registration-completion.html", templatename=templatename,config=default_settings, _scheme="https") 



@dealer_views_bp.route("/workflow-approvals", methods=["GET","POST"])  
@is_authenticated
def workflow_approvals():
    
    workflow_list = []
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    user = okta_admin.get_user(user_info["sub"])
    user_id=user["id"]
    
    #On a GET display the registration page with the defaults    
    if request.method == "GET":
        admin_groups = okta_admin.get_user_groups(user_id)
        #User organization attribute contains workflow request
        #FOR DEALERSHIP ASSOCIATION request
        #FOR ADMIN REQUEST find users that match the admin's group_id
        for item in admin_groups:
            if item["profile"]["name"] == "DEALER_ADMIN":
                admin_group_id=item["id"]
            if item["profile"]["name"].startswith("_LOC_"):
                location_group_id = item["id"]
        
        user_get_response = okta_admin.get_user_list_by_search('profile.organization eq "{location_group_id}" or profile.organization eq "{admin_group_id}" '
        .format(location_group_id=location_group_id, admin_group_id=admin_group_id))
        
        print(user_get_response)
        
        for idx, list in enumerate(user_get_response,start=1):
            group_get_response = okta_admin.get_group(id = list["profile"]["organization"])
            print(group_get_response)
            workflow_list.append({"id": idx, "requestor": list["profile"]["login"], 
            "request": group_get_response["profile"]["description"], "usr_grp":{"user_id":list["id"],"group_id": list["profile"]["organization"] } })
        
        print(workflow_list)
        
        return render_template(templatename+"/workflow-approvals.html", templatename=templatename,workflow_list=workflow_list, config=default_settings,_scheme="https")
    
    if request.method == "POST":
        if request.form.get("reject"):
            print("Reject " + request.form.get("reject"))
            req = request.form.get("reject")
            req = req.replace("\'", "\"")
            req = json.loads(req)
            user_id =req["user_id"]
            group_id =req["group_id"]
            
            #Remove user attribute organization ( as the request has been rejected)
            user_data = {
                "profile": {
                    "organization": ""
                }
            }
            okta_admin.update_user(user_id=user_id, user=user_data)
            
        if request.form.get("approve"):
            print("Approve " + request.form.get("approve"))
            req = request.form.get("approve")
            req = req.replace("\'", "\"")
            req = json.loads(req)
            user_id =req["user_id"]
            group_id =req["group_id"]
            
            #Assign user to group
            user_assign_response = okta_admin.assign_user_to_group(group_id,user_id)
            
            #Remove user attribute organization ( as the request has been approved)
            user_data = {
                "profile": {
                    "organization": ""
                }
            }
            okta_admin.update_user(user_id=user_id, user=user_data)
             
        return render_template(templatename+"/workflow-approvals.html", templatename=templatename,workflow_list=workflow_list, config=default_settings,_scheme="https")

@is_authenticated
@dealer_views_bp.route("/workflow-requests", methods=["GET","POST"])  
def workflow_requests():
    
    user_info = login.get_user_info() 
    okta_admin = OktaAdmin(default_settings)
    user = okta_admin.get_user(user_info["sub"])
    user_id=user["id"]
    
    workflow_list = []
    
    #On a GET display the registration page with the defaults    
    if request.method == "GET":
        
        list_group_user = [] 
        list_group_full = []
        
        #Find the groups the user belongs to
        get_user_groups_response = okta_admin.get_user_groups(user_id = user_id)
        #print(get_user_groups_response)
        for item in get_user_groups_response:
            if  item["profile"]["name"] != "Everyone": #Ignore the Everyone group
                list_group_user.append({"id": item["id"], "name" : item["profile"]["name"], "description" : item["profile"]["description"] })
           
        #Find the groups for this portal that start with name "DEALER_"
        get_groups = okta_admin.get_groups_by_name("DEALER_")
        #print(get_groups)
        for item in get_groups:
            list_group_full.append({"id": item["id"], "name" : item["profile"]["name"], "description" : item["profile"]["description"] })
        
        #Populate the workflow list with groups that the user is absent in
        set_list1 = set(tuple(sorted(d.items())) for d in list_group_full)
        set_list2 = set(tuple(sorted(d.items())) for d in list_group_user)
        set_difference = set_list1 - set_list2
        for tuple_element in set_difference:
            workflow_list.append(dict((x, y) for x, y in tuple_element))
     
        return render_template(templatename+"/workflow-requests.html", templatename=templatename,workflow_list=workflow_list, config=default_settings,_scheme="https")
    if request.method == "POST":
        if request.form.get("request_access"):
            print("request_access " + request.form.get("request_access"))
            group_id =request.form.get("request_access")
            
            #Remove user attribute organization ( as the request has been rejected)
            user_data = {
                "profile": {
                    "organization": group_id
                }
            }
            okta_admin.update_user(user_id=user_id, user=user_data)
        
        #Send Activation Email to the Admin
        subject_admin = "A workflow request was received"
        message_admin = ("A new request for access was received. The request is awaiting your approval. Click this link to log into your account <br />"
                      "<a href='{activation_link}'>{activation_link}</a> to review the request").format(
                activation_link=url_for( "dealer_views_bp.workflow_approvals",_external=True, _scheme="https"))
        send_email_response_admin = emailAllMembersOfGroup(group_id="00g3jy1jatm7h3CI7357", subject=subject_admin, message=message_admin)
            
        return render_template(templatename+"/workflow-requests.html", templatename=templatename,workflow_list=workflow_list, config=default_settings,_scheme="https")


#Email recipients who are member of a group      
def emailAllMembersOfGroup(group_id, subject, message):
    okta_admin = OktaAdmin(default_settings)

    #Find All members that will be notified
    recipients=[]
    user_list = okta_admin.get_user_list_by_group_id(group_id)
    for user in user_list:
        recipients.append( {"address": user["profile"]["email"]})
    
    if recipients:
        email_send = Email.send_mail(subject=subject,message=message,recipients=recipients)
        return email_send