from distutils.command.config import config
import logging
from os import access
import random
import string
import uuid
import json


# import functions
from flask import jsonify, render_template, session, request, json
from flask import Blueprint, url_for, redirect
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, get_udp_ns_fieldname, apply_remote_config
from utils.okta import TokenUtil, OktaAdmin, OktaAuth, OktaUtil, PKCE
from utils.rest import RestUtil

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo, gvalidation_bp_error, check_okta_api_token, check_zartan_config

logger = logging.getLogger(__name__)

# set blueprint
zartantv_views_bp = Blueprint('zartantv_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@zartantv_views_bp.route("/devicepage")
@apply_remote_config
def zartantv_devicepage():
    logger.debug("zartantv_devicepage()")
    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    client_id = get_device_client_id()
    appname = app_config["settings"]["app_deviceflow_appname"]

    id_token = ""
    access_token = ""
    refresh_token = ""
    reset_tokens = "false"

    return render_template(
        "zartantv/devicepage.html",
        user_info=get_userinfo(),
        id_token=id_token,
        access_token=access_token,
        refresh_token=refresh_token,
        reset_tokens=reset_tokens,
        client_id=client_id,
        appname=appname,
        config=app_config
    )


# Step 1.
# POST issuer/v1/device/authorize
@zartantv_views_bp.route("/deviceauthorization")
@apply_remote_config
def zartantv_deviceauthorization():
    logger.debug("zartantv_deviceauthorization()")
    #device_id = PKCE.generate_code_verifier(64)
    issuer = get_issuer()
    client_id = get_device_client_id()
    client_secret = get_device_client_secret()
    url = (
        "{issuer}/v1/device/authorize?"
        "client_id={client_id}&"
        "client_secret={client_secret}&"
        "scope=openid+profile+email+offline_access"
    ).format(
        issuer=issuer,
        client_id=client_id,
        client_secret=client_secret
    )
    response = RestUtil.execute_post(url)
    logger.debug("Device authorization response: {0}".format(response))
    return response


# Step 2.
# POST issuer/v1/token
# once we get a token back, be sure to update the user's profile
# with the device ID from the refresh token
@zartantv_views_bp.route("/token")
@apply_remote_config
def zartantv_token():
    logger.debug("zartantv_token()")
    issuer = get_issuer()
    client_id = get_device_client_id()
    client_secret = get_device_client_secret()
    device_code = request.args.get("device_code")
    url = (
        "{issuer}/v1/token?"
        "client_id={client_id}&"
        "client_secret={client_secret}&"
        "device_code={device_code}&"
        "grant_type=urn:ietf:params:oauth:grant-type:device_code"
    ).format(
        issuer=issuer,
        client_id=client_id,
        client_secret=client_secret,
        device_code=device_code
    )

    headers = OktaUtil.get_oauth_okta_headers(headers=None)
    body = {}
    response = RestUtil.execute_post(url, body, headers)
    logger.debug("v1/token response: {0}".format(response))
    return response


@zartantv_views_bp.route("/complete_registration", methods=["POST"])
@apply_remote_config
def zartantv_complete_registration():
    logger.debug("zartantv_complete_registration()")
    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    okta_admin = OktaAdmin(app_config)
    client_id = get_device_client_id()
    body = request.get_json()
    id_token = body["id_token"]
    device_code = body["device_code"]
    user_id = TokenUtil.get_single_claim_from_token(id_token, "sub")
    device_fieldname = get_udp_ns_fieldname("authorized_devices")

    user_app_profile = okta_admin.get_user_application_by_client_id(user_id, client_id)
    devices = []
    if device_fieldname in user_app_profile["profile"]:
        devices = user_app_profile["profile"][device_fieldname]
        if devices is None:
            devices = []
    else:
        devices = []

    devices.append(device_code)
    user_data = {
        "profile": {
            device_fieldname: devices
        }
    }
    okta_admin.update_application_user_profile_by_clientid(user_id, user_data, client_id)
    response = {
        "status": "OK",
        "messsage": "Device code [{0}] registered to {1}".format(device_code, user_id)
    }
    return jsonify(response)


@zartantv_views_bp.route("/verify_token", methods=["POST"])
@apply_remote_config
def zartantv_verify_token():
    logger.debug("zartantv_verify_token()")
    response = "false"
    body = request.get_json()
    logger.debug("Got JSON: {0}".format(body))

    try:
        access_token = body["access_token"]
        id_token = body["id_token"]
        refresh_token = body["refresh_token"]
        device_code = body["device_code"]

        # we need the ID token because we're using 
        # user profile storage to fake a backend DB
        # that stores user -> device mappings
        devices = get_authorized_devices(id_token)
        if device_code in devices:
            logger.debug("we found a device mapped to this user, check it's token")
            if is_token_valid(access_token, "access_token"):
                logger.debug("access token is good")
                response = "true"
            else:
                # access token is expired/invalid
                # use the refresh token to get another one
                logger.debug("access token is expired. try to get a new one using the refresh token")
                if is_token_valid(refresh_token, "refresh_token"):
                    logger.debug("refresh token is good, getting a new access token")
                    tokens = get_authtoken(refresh_token, "openid profile email offline_access")
                    response = tokens
                else:
                    logger.debug("refresh token is invalid, expired or has been revoked")
                    response = "false"
        else:
            logger.debug("a device was found, but not in the list?")
            response = "false"
        
        return response

    except Exception as e:
        logger.debug("No tokens found in request body")
        logger.debug("Exception: {0}".format(e))
        return response


def get_authorized_devices(id_token):
    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    okta_admin = OktaAdmin(app_config)
    id_token_claims = TokenUtil.get_claims_from_token(id_token)
    user_id = id_token_claims["sub"]
    client_id = id_token_claims["aud"]
    devices_fieldname = get_udp_ns_fieldname("authorized_devices")
    user_app_profile = okta_admin.get_user_application_by_client_id(user_id, client_id)
    devices = []

    if devices_fieldname in user_app_profile["profile"]:
        devices = user_app_profile["profile"][devices_fieldname]

    logger.debug("Got devices: {0}".format(devices))
    return devices


def is_token_valid(token, token_type_hint):
    if token in (None, ""):
        return False

    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    okta_auth = OktaAuth(app_config)
    client_id = get_device_client_id()
    client_secret = get_device_client_secret()
    introspect_response = okta_auth.introspect_with_clientid(token, token_type_hint, client_id, client_secret)
    logger.debug("introspect_response: {0}".format(introspect_response))
    #return introspect_response
    return introspect_response["active"] == True


def get_issuer():
    return session[SESSION_INSTANCE_SETTINGS_KEY]["issuer"]


def get_device_client_id():
    return session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientid"]


def get_device_client_secret():
    return session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientsecret"]


# trade in a refresh token for a new access token
def get_authtoken(refresh_token, scopes, headers=None):
    logger.debug("get_authtoken()")
    issuer = get_issuer()
    client_id = get_device_client_id()
    client_secret = get_device_client_secret()
    okta_headers = OktaUtil.get_oauth_okta_headers(headers, client_id, client_secret)
    url = (
        "{issuer}/v1/token?"
        "grant_type=refresh_token&"
        "scopes={scopes}&"
        "refresh_token={refresh_token}&"
    ).format(
        issuer=issuer,
        scopes=scopes,
        refresh_token=refresh_token
    )

    body = {}
    return RestUtil.execute_post(url, body, okta_headers)
    

@zartantv_views_bp.route("/revoketoken", methods=["POST"])
@apply_remote_config
def zartantv_revoketoken():
    logger.debug("zartantv_revoketoken()")
    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    okta_auth = OktaAuth(app_config)
    client_id = get_device_client_id()
    client_secret = get_device_client_secret()
    token = request.form["token"]
    logger.debug("****** Revoking token {0}".format(token))
    okta_auth.revoke_token_with_clientid(token, "refresh_token", client_id, client_secret)
    #status = is_token_valid(token, "refresh_token")
    #logger.debug("In revoke token... {0}".format(status))
    return "Completed"


# Required for Login Landing Page
@zartantv_views_bp.route("/profile")
@apply_remote_config
@is_authenticated
def zartantv_profile():
    logger.debug("zartantv_profile()")
    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    return render_template(
        "zartantv/profile.html",
        user_info=get_userinfo(),
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        config=app_config
    )


@zartantv_views_bp.route("/mydevices")
@apply_remote_config
@is_authenticated
def zartantv_mydevices():
    logger.debug("zartantv_mydevices()")
    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    user_info = get_userinfo()
    user_id = user_info["sub"]
    okta_admin = OktaAdmin(app_config)
    client_id = get_device_client_id()
    user_app_profile = okta_admin.get_user_application_by_client_id(user_id, client_id)
    device_fieldname = get_udp_ns_fieldname("authorized_devices")
    devices = []

    if device_fieldname in user_app_profile["profile"]:
        devices = user_app_profile["profile"][device_fieldname]

        if devices is None:
            devices = []

    logger.debug(devices)

    return render_template(
        "zartantv/mydevices.html",
        user_info=get_userinfo(),
        devices=devices,
        config=app_config
    )


@zartantv_views_bp.route("/removedevice")
@apply_remote_config
@is_authenticated
def zartantv_removedevice():
    logger.debug("zartantv_removedevice()")
    app_config = session[SESSION_INSTANCE_SETTINGS_KEY]
    user_info = get_userinfo()
    user_id = user_info["sub"]
    device_id = request.args.get('device_id')
    okta_admin = OktaAdmin(app_config)
    client_id = get_device_client_id()
    user_app_profile = okta_admin.get_user_application_by_client_id(user_id, client_id)
    device_fieldname = get_udp_ns_fieldname("authorized_devices")
    devices = []

    if device_fieldname in user_app_profile["profile"]:
        devices = user_app_profile["profile"][device_fieldname]

        if devices is None:
            devices = []
        else:
            devices.remove(device_id)

    user_data = {
        "profile": {
            device_fieldname: devices
        }
    }
    okta_admin.update_application_user_profile_by_clientid(user_id, user_data, client_id)

    redirect_url = url_for(
        "zartantv_views_bp.zartantv_mydevices",
        _external=True,
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])

    return redirect(redirect_url)
