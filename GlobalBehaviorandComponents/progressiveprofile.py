import logging

# import functions
from flask import Blueprint, request, session
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, apply_remote_config
from utils.okta import OktaAdmin

from GlobalBehaviorandComponents.validation import is_authenticated

logger = logging.getLogger(__name__)

# set blueprint
gbac_progressiveprofile_bp = Blueprint('gbac_progressiveprofile_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


@gbac_progressiveprofile_bp.route("/progressiveprofile", methods=["POST"])
@apply_remote_config
@is_authenticated
def progressiveprofile_bp():
    logger.debug("progressiveprofile_bp_profile()")

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    street = safe_get_dict(request.form, 'street')
    city = safe_get_dict(request.form, 'city')
    state = safe_get_dict(request.form, 'state')
    postal = safe_get_dict(request.form, 'postal')
    userid = safe_get_dict(request.form, 'userid')

    user_data = {"profile": {
        "streetAddress": street,
        "city": city,
        "state": state,
        "zipCode": postal
    }}

    user_update_response = okta_admin.update_user(userid, user_data)
    if "error" in user_update_response:
        message = "Error During Update: " + user_update_response
    else:
        message = user_update_response

    return message


@gbac_progressiveprofile_bp.route("/userprofile", methods=["POST"])
@apply_remote_config
@is_authenticated
def progressiveprofile_userprofile_bp():
    logger.debug("progressiveprofile_userprofile_bp()")

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    userid = safe_get_dict(request.form, 'userid')

    user_response = okta_admin.get_user(userid)
    if "error" in user_response:
        message = "Error Getting Profile: " + user_response
    else:
        message = user_response

    return message


def safe_get_dict(mydict, key):
    myval = ""
    mydictval = mydict.get(key)
    if mydictval:
        if mydictval.strip() != "":
            myval = mydictval.strip()
    return myval
