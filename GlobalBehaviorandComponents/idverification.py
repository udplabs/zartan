import logging
import datetime
import time

from flask import session
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_udp_ns_fieldname
from utils.okta import OktaAdmin, OktaUtil
from utils.rest import RestUtil

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
gbac_idverification_bp = Blueprint('gbac_idverification_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@gbac_idverification_bp.route("/getverificationcode")
@is_authenticated
def gbac_idverification_getverificationcode():
    logger.debug("gbac_idverification_bp")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    evidenttoken = ""

    basicauth = OktaUtil.get_encoded_auth("okta", "Ry4EZf8SyxKyStLK6BqxBBLXEW4SrIo6hc0m2rR3PoI")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic {0}".format(basicauth)
    }

    my_str = user["profile"]["email"]
    idx = my_str.index("@")
    email = my_str[:idx] + str(time.time()) + my_str[idx:]

    body = {
        "email": email,
        "templateId": "1ce55f4e-7bb2-4907-9643-dc61f1f04f4d"
    }

    response = RestUtil.execute_post(" https://verify.api.demo.evidentid.com/api/v1/verify/requests", headers=headers, body=body)
    evidenttoken = response["userIdentityToken"]
    user_data = {"profile": {get_udp_ns_fieldname("evident_id"): response["id"]}}
    okta_admin.update_user(user["id"], user_data)

    return evidenttoken


@gbac_idverification_bp.route("/updateidentity")
@is_authenticated
def gbac_idverification_updateidentity():
    logger.debug("gbac_idverification_updateidentity")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])

    basicauth = OktaUtil.get_encoded_auth("okta", "Ry4EZf8SyxKyStLK6BqxBBLXEW4SrIo6hc0m2rR3PoI")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic {0}".format(basicauth)
    }

    evident_id = user["profile"][get_udp_ns_fieldname("evident_id")]
    response = RestUtil.execute_get("https://verify.api.demo.evidentid.com/api/v1/verify/requests/{0}".format(evident_id), headers=headers)
    now = datetime.datetime.now()
    # dd/mm/YY H:M:S
    verifydate = now.strftime("%d/%m/%Y %H:%M:%S")

    user_data = {
        "profile": {
            get_udp_ns_fieldname("last_verified_date"): str(verifydate)
        }
    }
    status = ""

    for item in response["attributes"]:
        status = item["status"]
        if status == "pending":
            break

        if item["type"] == "core.firstname":
            user_data["profile"]["firstName"] = item["values"][0]
        if item["type"] == "core.lastname":
            user_data["profile"]["lastName"] = item["values"][0]
        if item["type"] == "core.address.zipcode":
            user_data["profile"]["zipCode"] = item["values"][0]
        if item["type"] == "core.address.city":
            user_data["profile"]["city"] = item["values"][0]
        if item["type"] == "core.address.state":
            user_data["profile"]["state"] = item["values"][0]
    if status == "pending":
        return status
    else:
        logging.debug(user_data)
        okta_admin.update_user(user["id"], user_data)
    return response


@gbac_idverification_bp.route("/isverified")
@is_authenticated
def gbac_idverification_isverified():
    logger.debug("gbac_idverification_isverified")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    verified_date = user["profile"][get_udp_ns_fieldname("last_verified_date")]
    return verified_date
