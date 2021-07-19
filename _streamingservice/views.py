import logging
import random
import string
import uuid
import json

# import functions
from flask import render_template, session, request
from flask import Blueprint, url_for, redirect
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config
from utils.okta import TokenUtil, OktaAdmin, OktaAuth, OktaUtil, PKCE
from utils.rest import RestUtil
from device_detector import DeviceDetector

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo, gvalidation_bp_error, check_okta_api_token, check_zartan_config

logger = logging.getLogger(__name__)

# set blueprint
streamingservice_views_bp = Blueprint('streamingservice_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@streamingservice_views_bp.route("/devicepage")
@apply_remote_config
def streamingservice_devicepage():
    logger.debug("streamingservice_devicepage()")
    client_id = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientid"]
    appname = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_appname"]
    applogo = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_applogo"]

    id_token = ""
    access_token = ""
    refresh_token = ""
    reset_tokens = "false"

    return render_template(
        "streamingservice/devicepage.html",
        user_info=get_userinfo(),
        id_token=id_token,
        access_token=access_token,
        refresh_token=refresh_token,
        reset_tokens=reset_tokens,
        client_id=client_id,
        appname=appname,
        applogo=applogo,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@streamingservice_views_bp.route("/device")
@apply_remote_config
def streamingservice_device():
    logger.debug("streamingservice_device()")

    letters_and_numbers = string.ascii_uppercase + string.digits
    result_str = ''.join(random.choice(letters_and_numbers) for i in range(8))
    result_str = result_str.replace("0", "Z")
    result_str = result_str.replace("O", "Z")
    result_str = result_str.replace("I", "L")
    user_code = result_str[:4] + '-' + result_str[4:]

    code_length = 64
    device_code = PKCE.generate_code_verifier(code_length)
    code_length2 = 64
    device_id = PKCE.generate_code_verifier(code_length2)

    verification_uri = url_for(
        "streamingservice_views_bp.streamingservice_device_activate",
        _external=True,
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]
    )

    expires_in = 800
    interval = 2

    url = "https://jl0tn0gk0e.execute-api.us-east-2.amazonaws.com/default/prd-zartan-deviceinformation"
    headers = {
        "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
    }
    body = {
        "device_code": device_code,
        "device_id": device_id,
        "user_code": user_code,
        "verification_uri": verification_uri,
        "expires_in": expires_in,
        "interval": interval,
    }
    RestUtil.execute_post(url, body, headers=headers)

    return body


@streamingservice_views_bp.route("/token")
@apply_remote_config
def streamingservice_token():
    logger.debug("streamingservice_token()")

    device_code = request.args.get('device_code')

    url = "https://sngfyrr4b2.execute-api.us-east-2.amazonaws.com/default/prd-zartan-devicetoken?device_code=" + device_code
    headers = {
        "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
    }
    s3response = RestUtil.execute_get(url, headers=headers)

    if "device_code" in s3response:
        response = s3response
    else:
        response = {
            "error": "authorization_pending"
        }

    return response


@streamingservice_views_bp.route("/revoketoken", methods=["POST"])
@apply_remote_config
def streamingservice_revoketoken():
    logger.debug("streamingservice_revoketoken()")

    client_id = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientid"]
    client_secret = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientsecret"]

    token = request.form['token']
    tokenhint = request.form['tokenhint']

    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    okta_auth.revoke_token_with_clientid(token, client_id=client_id, client_secret=client_secret, token_type_hint=tokenhint)

    return "Completed"


@streamingservice_views_bp.route("/token_check", methods=["POST"])
@apply_remote_config
def streamingservice_token_check():
    logger.debug("streamingservice_token_check()")
    response = "false"
    try:
        access_token = request.form['access_token']
        id_token = request.form['id_token']
        refresh_token = request.form['refresh_token']
        device_id = request.form['device_id']
        client_id = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientid"]
        client_secret = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientsecret"]
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

        isactiveID = okta_auth.introspect_with_clientid(id_token, client_id=client_id, client_secret=client_secret, token_type_hint="idtoken")

        devices_list = okta_admin.get_user_list_by_search("profile.login+eq+%22" + device_id + "@okta.com" + "%22")
        device_info = devices_list[0]

        if isactiveID["active"]:
            id_token_info = TokenUtil.get_claims_from_token(id_token)
            linkeddevices = okta_admin.get_linked_users(userid=id_token_info["sub"], name="device")
            ua = request.headers.get('User-Agent')
            # Parse UA string and load data to dict of 'os', 'client', 'device' keys
            device = DeviceDetector(ua).parse()
            logger.debug(device.device_brand_name())
            logger.debug(device.device_brand())
            logger.debug(device.device_model())

            isactiveAT = okta_auth.introspect_with_clientid(access_token, client_id=client_id, client_secret=client_secret, token_type_hint="access_token")
            if device_info["id"] in json.dumps(linkeddevices) and device_info["status"] == "ACTIVE":
                if "device_info_completed" not in device_info["profile"]:
                    user_data = {
                        "profile": {
                            "device_info_completed": "true",
                            "device_type": device.device_brand_name() + " " + device.device_type().title(),
                        }
                    }
                    okta_admin.update_user(user_id=device_info["id"], user=user_data)

                if isactiveAT["active"]:
                    response = "true"
                else:
                    isactiveRT = okta_auth.introspect_with_clientid(
                        refresh_token,
                        client_id=client_id,
                        client_secret=client_secret,
                        token_type_hint="refresh_token"
                    )

                    if isactiveRT['active']:
                        logging.debug("get new AT")

                        responseurl = url_for(
                            "streamingservice_views_bp.streamingservice_devicepage",
                            _external=True,
                            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]
                        )

                        tokens = get_authtoken(
                            headers=None,
                            refresh_token=refresh_token,
                            client_id=client_id, client_secret=client_secret,
                            grant_type="refresh_token",
                            redirect_uri=responseurl,
                            scopes="openid profile email offline_access",
                            device_id=device_id
                        )
                        response = tokens
                    else:
                        response = "false"
            else:
                response = "false"
        else:
            response = "false"
    finally:
        return response


@streamingservice_views_bp.route("/device_activate")
@apply_remote_config
@check_okta_api_token
@check_zartan_config
def streamingservice_device_activate():
    logger.debug("streamingservice_device_activate()")
    return render_template(
        "streamingservice/device_activate.html",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@streamingservice_views_bp.route("/device_validatecode", methods=["POST"])
@apply_remote_config
def streamingservice_device_validatecode():
    logger.debug("streamingservice_device_validatecode()")

    url = "https://jl0tn0gk0e.execute-api.us-east-2.amazonaws.com/default/prd-zartan-deviceinformation?user_code=" + request.form["user_code"]
    headers = {
        "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
    }
    s3response = RestUtil.execute_get(url, headers=headers)

    if ("device_code" in s3response):
        logger.debug("Save Device State")
        state = str(uuid.uuid4())
        session["device_state"] = state

        url = "https://d9qgirtrci.execute-api.us-east-2.amazonaws.com/default/prd-zartan-devicestate"
        headers = {
            "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
        }
        body = {
            "device_code": s3response['device_code'],
            "device_id": s3response['device_id'],
            "state": state
        }
        RestUtil.execute_post(url, body, headers=headers)

        response = url_for(
            "streamingservice_views_bp.streamingservice_device_register",
            _external=True,
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]
        )

    else:
        response = "invalid"
    return response


@streamingservice_views_bp.route("/device_register")
@apply_remote_config
def streamingservice_device_register():
    logger.debug("streamingservice_device_register()")
    client_id = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientid"]
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    idplist = okta_admin.get_idps()
    facebook = ""
    google = ""
    linkedin = ""
    microsoft = ""
    idp = ""
    idptype = ""
    appname = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_appname"]
    if appname is None:
        appname = ""

    for idp in idplist:
        if idp["type"] == "FACEBOOK":
            facebook = idp["id"]
            idp = "true"
        elif idp["type"] == "GOOGLE":
            google = idp["id"]
            idp = "true"
        elif idp["type"] == "LINKEDIN":
            linkedin = idp["id"]
            idp = "true"
        elif idp["type"] == "MICROSOFT":
            microsoft = idp["id"]
            idp = "true"
        elif idp["type"] == "SAML2":
            idptype = "SAML2"
            idp = "true"

    url = "https://d9qgirtrci.execute-api.us-east-2.amazonaws.com/default/prd-zartan-devicestate?state={0}".format(session["device_state"])
    headers = {
        "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
    }
    s3response = RestUtil.execute_get(url, headers=headers)
    del s3response['state']
    return render_template(
        "streamingservice/device_register.html",
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        state=session["device_state"],
        facebook=facebook,
        google=google,
        linkedin=linkedin,
        microsoft=microsoft,
        idp=idp,
        idptype=idptype,
        appname=appname,
        client_id=client_id,
        deviceinfo=json.dumps(s3response, sort_keys=True, indent=4))


@streamingservice_views_bp.route('/authorization-code/callback', methods=["POST"])
@apply_remote_config
def streamingservice_callback():
    """ handler for the oidc call back of the app """
    logger.debug("streamingservice_callback()")
    response = None
    has_app_level_mfa_policy = False
    client_id = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientid"]
    client_secret = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_clientsecret"]

    if "code" in request.form:
        oidc_code = request.form["code"]
        oidc_state = request.form["state"]
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        oauth_token = get_oauth_token_from_login(
            code=oidc_code,
            grant_type="authorization_code",
            auth_options={
                "client_id": client_id,
                "client_secret": client_secret,
            }
        )

        url = "https://d9qgirtrci.execute-api.us-east-2.amazonaws.com/default/prd-zartan-devicestate?state={0}".format(oidc_state)
        headers = {
            "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
        }
        s3response = RestUtil.execute_get(url, headers=headers)

        url = "https://sngfyrr4b2.execute-api.us-east-2.amazonaws.com/default/prd-zartan-devicetoken"
        headers = {
            "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
        }
        body = {
            "device_code": s3response["device_code"],
            "device_id": s3response["device_id"],
            "access_token": oauth_token["access_token"],
            "id_token": oauth_token['id_token'],
            "refresh_token": oauth_token['refresh_token']
        }
        RestUtil.execute_post(url, body, headers=headers)

        user = okta_auth.introspect_with_clientid(oauth_token['id_token'], client_id=client_id, client_secret=client_secret, token_type_hint="idtoken")

        responseurl = url_for(
            "streamingservice_views_bp.streamingservice_device_complete",
            _external=True,
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"]
        )

        responseurl = responseurl + "?device_id={deviceid}&user_id={userid}&device_code={devicecode}".format(
            deviceid=s3response["device_id"],
            userid=user["sub"],
            devicecode=s3response["device_code"])

        response = redirect(responseurl)

    elif "error" in request.form:
        # This is in the case there is an Okta App level MFA policy
        logger.error("ERROR: {0}, MESSAGE: {1}".format(request.form["error"], request.form["error_description"]))
        if ("The client specified not to prompt, but the client app requires re-authentication or MFA." == request.form["error_description"]):
            has_app_level_mfa_policy = True

        # Error occured with Accessing the app instance
        if has_app_level_mfa_policy:
            error_message = "Failed to Authenticate.  Please remove App Level MFA Policy and use a Global MFA Policy. Error: {0} - {1}".format(
                request.form["error"],
                request.form["error_description"]
            )
            response = gvalidation_bp_error(error_message)
        else:
            error_message = "Failed to Authenticate.  Check to make sure the user has access to the application. Error: {0} - {1}".format(
                request.form["error"],
                request.form["error_description"]
            )

            response = gvalidation_bp_error(error_message)
    else:
        # catch all error
        response = gvalidation_bp_error("Failed to Authenticate.  Check to make sure the user has access to the application.")

    return response


@streamingservice_views_bp.route("/device_complete")
@apply_remote_config
def streamingservice_device_complete():
    logger.debug("streamingservice_device_complete()")

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    parent_id = request.args.get('user_id')
    device_id = request.args.get('device_id')
    first_name = "User"
    last_name = "Device"
    login = device_id + "@okta.com"
    linked_name = "device_owner"

    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    numbers = string.digits
    password = ''.join(random.choice(uppercase_letters) for i in range(4)) + \
        ''.join(random.choice(lowercase_letters) for i in range(4)) + \
        ''.join(random.choice(numbers) for i in range(4))

    user_data = {
        "profile": {
            "firstName": first_name,
            "lastName": last_name,
            "email": login,
            "login": login,
            "device_id": device_id
        },
        "credentials": {
            "password": {"value": password}
        },
        "groupIds": [],
        "type": {
            "id": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_deviceflow_deviceobject"]
        }
    }

    user_create_response = okta_admin.create_user(user_data, activate_user=True)
    logger.debug(user_create_response)
    if not parent_id == "None":
        logger.debug("ParentID Found")
        okta_admin.create_linked_users(user_create_response['id'], parent_id, linked_name)

        url = "https://sngfyrr4b2.execute-api.us-east-2.amazonaws.com/default/prd-zartan-devicetoken?device_code=" + request.args.get('device_code')
        headers = {
            "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
        }

        s3response = RestUtil.execute_get(url, headers=headers)
        del s3response['device_id']
        del s3response['device_code']

        return render_template(
            "streamingservice/device_complete.html",
            config=session[SESSION_INSTANCE_SETTINGS_KEY],
            deviceinfo=json.dumps(s3response, sort_keys=True, indent=4))
    else:

        redirect_url = url_for(
            "streamingservice_views_bp.streamingservice_device_activate",
            _external=True,
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])

        return redirect(redirect_url)


# Required for Login Landing Page
@streamingservice_views_bp.route("/profile")
@apply_remote_config
@is_authenticated
def streamingservice_profile():
    logger.debug("streamingservice_profile()")

    return render_template(
        "streamingservice/profile.html",
        user_info=get_userinfo(),
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@streamingservice_views_bp.route("/familymembers")
@apply_remote_config
@is_authenticated
def streamingservice_familymembers():
    logger.debug("streamingservice_familymembers()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    schemas = okta_admin.get_user_schemas_linkedobject()
    nfamily = ""
    logger.debug(schemas)
    if schemas:
        family = "["
        for schema in schemas:
            if schema['primary']['name'] == "streaming_owner":
                family = family + "{" + \
                    "\"pname\":\"" + schema['primary']['name'] + "\"," + \
                    "\"ptitle\":\"" + schema['primary']['title'] + "\"," + \
                    "\"aname\":\"" + schema['associated']['name'] + "\"," + \
                    "\"atitle\":\"" + schema['associated']['title'] + "\"," + \
                    "\"users\": [ "

                users = okta_admin.get_linked_users(user_info['sub'], schema['associated']['name'])

                for user in users:
                    userid = user['_links']['self']['href'].rsplit('/', 1)[-1]
                    associateduser = okta_admin.get_user(userid)
                    family = family + json.dumps(associateduser) + ","
                family = family[:-1] + "]},"

        family = family[:-1] + "]"
        logger.debug(family)
        nfamily = json.loads(family)

    return render_template(
        "streamingservice/familymembers.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        nfamily=nfamily)


@streamingservice_views_bp.route("/createusers")
@apply_remote_config
@is_authenticated
def streamingservice_create_page():
    logger.debug("streamingservice")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = request.args.get('user_id')
    user_info2 = okta_admin.get_user(user_id)
    parent_id = request.args.get('parent_id')
    linked_name = request.args.get('linked_name')

    return render_template(
        "streamingservice/createusers.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        user_info2=user_info2,
        parent_id=parent_id,
        linked_name=linked_name,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@streamingservice_views_bp.route("/createuser", methods=["POST"])
@apply_remote_config
def streamingservice_user_create():
    logger.debug("streamingservice_user_create")

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    login = request.form.get('email')
    mobile_phone = request.form.get('phonenumber')
    parent_id = request.form.get('parent_id')
    linked_name = request.form.get('linked_name')
    user_data = {"profile": {"firstName": first_name, "lastName": last_name, "email": email, "login": login, "mobilePhone": mobile_phone}}
    user_create_response = okta_admin.create_user(user_data, True)

    if "errorCode" not in user_create_response:
        msg = "User {0} {1} was Created".format(first_name, last_name)
    else:
        msg = "Error During Create - " + str(user_create_response["errorCauses"][0]["errorSummary"])

    okta_admin.create_linked_users(user_create_response['id'], parent_id, linked_name)
    return redirect(url_for(
        "streamingservice_views_bp.streamingservice_familymembers",
        _external="True",
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
        message=msg))


@streamingservice_views_bp.route("/updateuser", methods=["POST"])
@apply_remote_config
@is_authenticated
def streamingservice_user_update():
    logger.debug("gbac_user_update")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = request.form.get('user_id')
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    email = request.form.get('email')
    mobile_phone = request.form.get('phonenumber')

    user_data = {"profile": {"firstName": first_name, "lastName": last_name, "email": email, "mobilePhone": mobile_phone}}
    user_update_response = okta_admin.update_user(user_id, user_data)

    if user_update_response:
        message = "User {0} {1} was Updated".format(first_name, last_name)
    else:
        message = "Error During Update"

    return redirect(
        url_for(
            "streamingservice_views_bp.streamingservice_familymembers",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=user_id,
            message=message))


@streamingservice_views_bp.route("/mydevices")
@apply_remote_config
@is_authenticated
def streamingservice_mydevices():
    logger.debug("streamingservice_mydevices()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    schemas = okta_admin.get_user_schemas_linkedobject()
    nfamily = ""
    logger.debug(schemas)
    if schemas:
        family = "["
        for schema in schemas:
            if schema['primary']['name'] == "device_owner":
                family = family + "{" + \
                    "\"pname\":\"" + schema['primary']['name'] + "\"," + \
                    "\"ptitle\":\"" + schema['primary']['title'] + "\"," + \
                    "\"aname\":\"" + schema['associated']['name'] + "\"," + \
                    "\"atitle\":\"" + schema['associated']['title'] + "\"," + \
                    "\"users\": [ "

                users = okta_admin.get_linked_users(user_info['sub'], schema['associated']['name'])

                for user in users:
                    userid = user['_links']['self']['href'].rsplit('/', 1)[-1]
                    associateduser = okta_admin.get_user(userid)
                    family = family + json.dumps(associateduser) + ","
                family = family[:-1] + "]},"

        family = family[:-1] + "]"
        logger.debug(family)
        nfamily = json.loads(family)

    return render_template(
        "streamingservice/mydevices.html",
        user_info=get_userinfo(),
        nfamily=nfamily,
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@streamingservice_views_bp.route("/suspenddevice")
@apply_remote_config
@is_authenticated
def streamingservice_device_suspend():
    logger.debug("streamingservice_device_suspend()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = request.args.get('user_id')
    suspend_user = okta_admin.suspend_user(user_id)

    if not suspend_user:
        message = "Device Suspended"
    else:
        message = "Error During Suspension"

    return redirect(url_for(
        "streamingservice_views_bp.streamingservice_mydevices",
        _external="True",
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
        message=message))


@streamingservice_views_bp.route("/unsuspenddevice")
@apply_remote_config
@is_authenticated
def streamingservice_device_unsuspend():
    logger.debug("streamingservice_device_unsuspend()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = request.args.get('user_id')
    unsuspend_user = okta_admin.unsuspend_user(user_id)

    if not unsuspend_user:
        message = "Device Un-Suspended"
    else:
        message = "Error During Un-Suspension"

    return redirect(url_for(
        "streamingservice_views_bp.streamingservice_mydevices",
        _external="True",
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"], message=message))


def get_oauth_token_from_login(code, grant_type, auth_options=None, headers=None):
    logger.debug("OktaAuth.get_oauth_token()")
    okta_headers = OktaUtil.get_oauth_okta_headers(headers)

    redirect_url = url_for("streamingservice_views_bp.streamingservice_callback", _external=True, _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])

    url = (
        "{issuer}/v1/token?"
        "grant_type={grant_type}&"
        "code={code}&"
        "redirect_uri={redirect_uri}"
    ).format(
        issuer=session[SESSION_INSTANCE_SETTINGS_KEY]["issuer"],
        code=code,
        redirect_uri=redirect_url,
        grant_type=grant_type
    )

    body = {
        "authorization_code": code
    }

    if auth_options:
        for key in auth_options:
            url = "{url}&{key}={value}".format(url=url, key=key, value=auth_options[key])

    return RestUtil.execute_post(url, body, okta_headers)


def get_authtoken(refresh_token, client_id, client_secret, grant_type, headers, redirect_uri, scopes, device_id):
    logger.debug("OktaAuth.get_oauth_token_from_refresh_token()")
    okta_headers = OktaUtil.get_oauth_okta_headers(headers, client_id, client_secret)

    url = (
        "{issuer}/v1/token?"
        "grant_type={grant_type}&"
        "redirect_uri={redirect_uri}&"
        "scopes={scopes}&"
        "refresh_token={refresh_token}&"
        "device_id={device_id}"
    ).format(
        issuer=session[SESSION_INSTANCE_SETTINGS_KEY]["issuer"],
        refresh_token=refresh_token,
        redirect_uri=redirect_uri,
        scopes=scopes,
        grant_type=grant_type,
        device_id=device_id
    )

    body = {}

    return RestUtil.execute_post(url, body, okta_headers)
