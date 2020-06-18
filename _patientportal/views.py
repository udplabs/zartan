import logging
import datetime
import time

from flask import render_template, session, request, redirect, url_for
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_udp_ns_fieldname
from utils.okta import TokenUtil, OktaAdmin, OktaUtil
from utils.rest import RestUtil
from GlobalBehaviorandComponents.mfaenrollment import get_enrolled_factors

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
patientportal_views_bp = Blueprint('patientportal_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@patientportal_views_bp.route("/profile")
@is_authenticated
def patientportal_profile():
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])

    if get_udp_ns_fieldname("consent") in user["profile"]:
        logging.debug(user)
        consent = user["profile"][get_udp_ns_fieldname("consent")]
        logging.debug(consent)
        if consent.strip() == "":
            consent = ''
            session['appointment'] = "No Appointments Currently Set."
    else:
        consent = ''
    logging.debug(consent)

    factors = get_enrolled_factors(user["id"])

    id_token = TokenUtil.get_id_token(request.cookies)
    patientid = TokenUtil.get_single_claim_from_token(id_token, "extPatientId")

    is_evident_validated = ""
    if get_udp_ns_fieldname("is_evident_validated") in user["profile"]:
        is_evident_validated = user["profile"][get_udp_ns_fieldname("is_evident_validated")]

    return render_template(
        "patientportal/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        user_info2=user,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        consent=consent,
        factors=factors,
        patientid=patientid,
        is_evident_validated=is_evident_validated)


@patientportal_views_bp.route("/acceptterms")
@is_authenticated
def patientportal_accept_terms():
    logger.debug("patientportal_accept_terms()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    user_id = user["id"]

    now = datetime.datetime.now()
    # dd/mm/YY H:M:S
    consent = now.strftime("%d/%m/%Y %H:%M:%S")

    user_data = {"profile": {get_udp_ns_fieldname("consent"): consent}}
    user_update_response = okta_admin.update_user(user_id, user_data)

    if user_update_response:
        message = "Thank you for completing the Consent Form."
    else:
        message = "Error During consent"

    return redirect(url_for("patientportal_views_bp.patientportal_profile", _external="True", _scheme="https", user_id=user_id, message=message))


@patientportal_views_bp.route("/account")
@is_authenticated
def patientportal_account():
    logger.debug("patientportal_account")
    return render_template(
        "patientportal/account.html",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@patientportal_views_bp.route("/schedule")
@is_authenticated
def patientportal_schedule():
    logger.debug("patientportal_schedule")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    dob = ""
    gender = ""
    if get_udp_ns_fieldname("dob") in user["profile"]:
        dob = user["profile"][get_udp_ns_fieldname("dob")]
    if get_udp_ns_fieldname("gender") in user["profile"]:
        gender = user["profile"][get_udp_ns_fieldname("gender")]

    return render_template(
        "patientportal/schedule.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        user_info2=user,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        dob=dob,
        gender=gender)


def safe_get_dict(mydict, key):
    myval = ""
    mydictval = mydict.get(key)
    if mydictval:
        if mydictval.strip() != "":
            myval = mydictval.strip()
    return myval


@patientportal_views_bp.route("/addschedule", methods=["POST"])
@is_authenticated
def patientportal_add_schedule():
    logger.debug("patientportal_add_schedule")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = request.form.get('user_id')

    first_name = safe_get_dict(request.form, 'firstname')
    last_name = safe_get_dict(request.form, 'lastname')
    email = safe_get_dict(request.form, 'email')
    address = safe_get_dict(request.form, 'address')
    city = safe_get_dict(request.form, 'city')
    state = safe_get_dict(request.form, 'state')
    zip_code = safe_get_dict(request.form, 'zipCode')
    country = safe_get_dict(request.form, 'country')
    dob = safe_get_dict(request.form, 'dob')
    hasvisited = safe_get_dict(request.form, 'hasvisited')
    mobile_phone = safe_get_dict(request.form, 'mobilePhone')
    gender = safe_get_dict(request.form, 'gender')

    if request.form.get('datepicker'):
        session['appointment'] = "Appointment set for " + request.form.get('datepicker') + " between the hours of " + request.form.get('timepicker')

    user_data = {"profile": {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "mobilePhone": mobile_phone,
        "streetAddress": address,
        "city": city,
        "state": state,
        "zipCode": zip_code,
        "countryCode": country,
        get_udp_ns_fieldname("dob"): dob,
        get_udp_ns_fieldname("hasvisited"): hasvisited,
        get_udp_ns_fieldname("gender"): gender,
    }}

    user_update_response = okta_admin.update_user(user_id, user_data)

    if "error" in user_update_response:
        message = "Error During Update: " + user_update_response
    else:
        message = "Appointment is scheduled!"

    return redirect(url_for("patientportal_views_bp.patientportal_profile", _external="True", _scheme="https", user_id=user_id, message=message))


@patientportal_views_bp.route("/updateuserinfo", methods=["POST"])
@is_authenticated
def patientportal_user_update():
    logger.debug("patientportal_user_update")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = request.form.get('user_id')
    logging.debug(request.form.to_dict())

    first_name = safe_get_dict(request.form, 'firstname')
    last_name = safe_get_dict(request.form, 'lastname')
    email = safe_get_dict(request.form, 'email')
    mobile_phone = safe_get_dict(request.form, 'mobilePhone')
    consent = safe_get_dict(request.form, 'nconsent')

    user_data = {"profile": {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "mobilePhone": mobile_phone,
        get_udp_ns_fieldname("consent"): consent,
    }}

    logging.debug(user_data)
    user_update_response = okta_admin.update_user(user_id, user_data)
    logging.debug(user_update_response)

    if "error" in user_update_response:
        message = "Error During Update: " + user_update_response
    else:
        message = "User Updated!"

    return redirect(url_for("patientportal_views_bp.patientportal_profile", _external="True", _scheme="https", user_id=user_id, message=message))


@patientportal_views_bp.route("/clearconsent/<userid>")
@is_authenticated
def patientportal_clear_consent(userid):
    logger.debug("patientportal_clear_consent")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    user_data = {"profile": {
        get_udp_ns_fieldname("consent"): "",
    }}

    user_update_response = okta_admin.update_user(userid, user_data)

    if "error" in user_update_response:
        message = "Error During Update: " + user_update_response
    else:
        message = ""

    return redirect(url_for("patientportal_views_bp.patientportal_profile", _external="True", _scheme="https", user_id=userid, message=message))


@patientportal_views_bp.route("/getverificationcode")
@is_authenticated
def patientportal_getverificationcode():
    logger.debug("patientportal_getverificationcode")
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


@patientportal_views_bp.route("/healthrecord")
@is_authenticated
def patientportal_healthrecord():
    logger.debug("patientportal_healthrecord")
    return render_template(
        "patientportal/healthrecord.html",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])
