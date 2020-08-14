import logging
import datetime
import json

from flask import render_template, session, request, redirect, url_for
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_udp_ns_fieldname
from utils.okta import TokenUtil, OktaAdmin
from GlobalBehaviorandComponents.mfaenrollment import get_enrolled_factors

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
consumerproducts_views_bp = Blueprint('consumerproducts_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@consumerproducts_views_bp.route("/profile")
@is_authenticated
def consumerproducts_profile():
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    userapp = okta_admin.get_user_application_by_current_client_id(user_info["sub"])

    if get_udp_ns_fieldname("consent") in userapp["profile"]:
        logging.debug(user)
        consent = userapp["profile"][get_udp_ns_fieldname("consent")]
        logging.debug(consent)
        if consent.strip() == "":
            consent = ''
    else:
        consent = ''
    logging.debug(consent)

    factors = get_enrolled_factors(user["id"])

    return render_template(
        "consumerproducts/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        user_info2=user,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        factors=factors,
        consent=consent)


# Required for Login Landing Page
@consumerproducts_views_bp.route("/discounts")
@is_authenticated
def consumerproducts_discounts():
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user_application_by_current_client_id(user_info["sub"])
    logging.debug(user)
    if get_udp_ns_fieldname("consent") in user["profile"]:
        logging.debug(user)
        consent = user["profile"][get_udp_ns_fieldname("consent")]
        logging.debug(consent)
        if consent.strip() == "":
            consent = ''
    else:
        consent = ''
    logging.debug(consent)

    return render_template(
        "consumerproducts/discounts.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        user_info2=user,
        consent=consent,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@consumerproducts_views_bp.route("/acceptterms")
@is_authenticated
def consumerproducts_accept_terms():
    logger.debug("consumerproducts_accept_terms()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    user_id = user["id"]

    now = datetime.datetime.now()
    # dd/mm/YY H:M:S
    consent = now.strftime("%d/%m/%Y %H:%M:%S")

    user_data = {"profile": {get_udp_ns_fieldname("consent"): consent}}
    user_update_response = okta_admin.update_application_user_profile(user_id, user_data)

    if user_update_response:
        message = "Thank you for completing the Consent Form."
    else:
        message = "Error During consent"

    return redirect(
        url_for(
            "consumerproducts_views_bp.consumerproducts_discounts",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=user_id,
            message=message))


def safe_get_dict(mydict, key):
    myval = ""
    mydictval = mydict.get(key)
    if mydictval:
        if mydictval.strip() != "":
            myval = mydictval.strip()
    return myval


@consumerproducts_views_bp.route("/updateprofile", methods=["POST"])
@is_authenticated
def consumerproducts_add_schedule():
    logger.debug("consumerproducts_updateprofile")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    country = safe_get_dict(request.form, 'country')
    dob = safe_get_dict(request.form, 'dob')
    gender = safe_get_dict(request.form, 'gender')

    user_data = {"profile": {
        "countryCode": country,
        get_udp_ns_fieldname("dob"): dob,
        get_udp_ns_fieldname("gender"): gender,
    }}

    user_update_response = okta_admin.update_user(user_info["sub"], user_data)

    if "errorCode" in user_update_response:
        message = "Error During Update: " + user_update_response["errorSummary"]
    else:
        message = "Thank you. Your Coupon was sent to your email on file!"

    return redirect(
        url_for(
            "consumerproducts_views_bp.consumerproducts_discounts",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            message=message))


@consumerproducts_views_bp.route("/updateuserinfo", methods=["POST"])
@is_authenticated
def consumerproducts_user_update():
    logger.debug("consumerproducts_user_update")
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

    return redirect(
        url_for(
            "consumerproducts_views_bp.consumerproducts_profile",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=user_id,
            message=message))


@consumerproducts_views_bp.route("/updatecomm/<comm>")
@is_authenticated
def consumerproducts_update_comm(comm):
    logger.debug("consumerproducts_update_comm")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_id = request.args.get('user_id')
    logging.debug(user_id)
    logging.debug(request.args.get('set'))
    user_data = {"profile": {
        get_udp_ns_fieldname(comm + "_comm"): request.args.get('set'),
    }}

    logging.debug(user_data)
    user_update_response = okta_admin.update_user(user_id, user_data)
    logging.debug(user_update_response)

    if "errorCode" in user_update_response:
        message = "Error During Update: " + user_update_response
    else:
        message = "Thank you! Your " + request.args.get('product') + " has been updated."

    return redirect(
        url_for(
            "consumerproducts_views_bp.consumerproducts_profile",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=user_id,
            message=message))


@consumerproducts_views_bp.route("/clearconsent/<userid>")
@is_authenticated
def consumerproducts_clear_consent(userid):
    logger.debug("consumerproducts_clear_consent")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    user_data = {"profile": {
        get_udp_ns_fieldname("consent"): "",
    }}

    user_update_response = okta_admin.update_application_user_profile(userid, user_data)

    if "error" in user_update_response:
        message = "Error During Update: " + user_update_response["errorSummary"]
    else:
        message = ""

    return redirect(
        url_for(
            "consumerproducts_views_bp.consumerproducts_profile",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=userid,
            message=message))


@consumerproducts_views_bp.route("/apps")
def consumerproducts_apps():
    logger.debug("consumerproducts_apps")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    app_info = okta_admin.get_applications_all()
    logging.debug(app_info)

    return json.dumps(app_info)
