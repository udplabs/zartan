import logging
import datetime

from flask import render_template, session, request, redirect, url_for
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_udp_ns_fieldname, apply_remote_config
from utils.okta import TokenUtil, OktaAdmin
from GlobalBehaviorandComponents.mfaenrollment import get_enrolled_factors

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

# SMART/FHIR Libraries
from utils.fhirclient import client
from utils.fhirclient.models.medicationrequest import MedicationRequest
from utils.fhirclient.models.claim import Claim
import uuid
import cachetools
import threading

# Server side cache for storing our FHIR tokens (to avoid making our session too big).
fhirStore = cachetools.TTLCache(maxsize=1000 * 1000, ttl=60 * 60 * 6)
fhirStoreLock = threading.Lock()


logger = logging.getLogger(__name__)

# set blueprint
healthcare_views_bp = Blueprint('healthcare_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@healthcare_views_bp.route("/profile")
@apply_remote_config
@is_authenticated
def healthcare_profile():
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
        "healthcare/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=get_userinfo(),
        user_info2=user,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        consent=consent,
        factors=factors,
        patientid=patientid,
        is_evident_validated=is_evident_validated)


@healthcare_views_bp.route("/acceptterms")
@apply_remote_config
@is_authenticated
def healthcare_accept_terms():
    logger.debug("healthcare_accept_terms()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])
    user_id = user["id"]

    now = datetime.datetime.now()
    # dd/mm/YY H:M:S
    consent = now.strftime("%d/%m/%Y %H:%M:%S")

    user_data = {"profile": {get_udp_ns_fieldname("consent"): consent}}
    user_update_response = okta_admin.update_user(user_id, user_data)
    logger.debug(user_update_response)

    return redirect(
        url_for(
            "healthcare_views_bp.healthcare_profile",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=user_id))


@healthcare_views_bp.route("/account")
@apply_remote_config
@is_authenticated
def healthcare_account():
    logger.debug("healthcare_account")
    return render_template(
        "healthcare/account.html",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@healthcare_views_bp.route("/schedule")
@apply_remote_config
@is_authenticated
def healthcare_schedule():
    logger.debug("healthcare_schedule")
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
        "healthcare/schedule.html",
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


@healthcare_views_bp.route("/addschedule", methods=["POST"])
@apply_remote_config
@is_authenticated
def healthcare_add_schedule():
    logger.debug("healthcare_add_schedule")
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

    return redirect(
        url_for(
            "healthcare_views_bp.healthcare_profile",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=user_id,
            message=message))


@healthcare_views_bp.route("/updateuserinfo", methods=["POST"])
@apply_remote_config
@is_authenticated
def healthcare_user_update():
    logger.debug("healthcare_user_update")
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
            "healthcare_views_bp.healthcare_profile",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=user_id,
            message=message))


@healthcare_views_bp.route("/clearconsent/<userid>")
@apply_remote_config
@is_authenticated
def healthcare_clear_consent(userid):
    logger.debug("healthcare_clear_consent")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    user_data = {"profile": {
        get_udp_ns_fieldname("consent"): "",
    }}

    user_update_response = okta_admin.update_user(userid, user_data)

    if "error" in user_update_response:
        message = "Error During Update: " + user_update_response
    else:
        message = ""

    return redirect(
        url_for(
            "healthcare_views_bp.healthcare_profile",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=userid,
            message=message))


@healthcare_views_bp.route("/healthrecord")
@apply_remote_config
@is_authenticated
def healthcare_healthrecord():
    logger.debug("healthcare_healthrecord")
    return render_template(
        "healthcare/healthrecord.html",
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@healthcare_views_bp.route("/healthins")
@apply_remote_config
@is_authenticated
def healthcare_healthins():
    logger.debug("healthcare_healthins")

    # app setup
    smartClient = _get_smart(request)
    accountLinked = False
    name = ""
    medications = []
    claims = []

    if smartClient.ready and smartClient.patient is not None:
        accountLinked = True
        smartClient.scope = smartClient.scope.replace(' skip_patient_selection', '')
        name = smartClient.human_name(smartClient.patient.name[0] if smartClient.patient.name and len(smartClient.patient.name) > 0 else 'Unknown')

        logger.debug(smartClient.authorized_scopes)

        if "patient/MedicationRequest.read" in smartClient.authorized_scopes:
            medSearch = MedicationRequest.where({'patient': smartClient.patient_id}).perform(smartClient.server)
            if medSearch.entry:
                for bundleEntry in medSearch.entry:
                    medEntry = {
                        "name": bundleEntry.resource.medicationCodeableConcept.text,
                        "dateIssued": bundleEntry.resource.authoredOn.date.strftime("%m/%d/%Y"),
                        "instructions": ""
                    }
                    if bundleEntry.resource.dosageInstruction:
                        medEntry["instructions"] = bundleEntry.resource.dosageInstruction[0].text

                    medications.append(medEntry)

        if "patient/Claim.read" in smartClient.authorized_scopes:
            claimSearch = Claim.where({'patient': smartClient.patient_id}).perform(smartClient.server)
            if claimSearch.entry:
                for bundleEntry in claimSearch.entry:
                    logger.info(bundleEntry.resource.item[0].productOrService.text)
                    logger.info(bundleEntry.resource.provider.display)
                    logger.info("{0} {1}".format(bundleEntry.resource.total.value, bundleEntry.resource.total.currency))
                    logger.info(bundleEntry.resource.billablePeriod.start.date.strftime("%m/%d/%Y"))
                    claimEntry = {
                        "purpose": bundleEntry.resource.item[0].productOrService.text,
                        "date": bundleEntry.resource.billablePeriod.start.date.strftime("%m/%d/%Y"),
                        "payee": bundleEntry.resource.provider.display,
                        "amount": "{value:.2f} {currency}".format(value=bundleEntry.resource.total.value, currency=bundleEntry.resource.total.currency)
                    }
                    claims.append(claimEntry)

    return render_template(
        "healthcare/healthins.html",
        user_info=get_userinfo(),
        patient_name=name,
        medication_info=medications,
        claim_info=claims,
        account_linked=accountLinked,
        authorize_url=smartClient.authorize_url,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


@healthcare_views_bp.route("/smartfhir_callback")
@apply_remote_config
@is_authenticated
def healthcare_smartfhir_callback():
    logger.debug("healthcare_smartfhir_callback")
    smartClient = _get_smart(request)
    try:
        smartClient.handle_callback(request.url)
        logger.info(smartClient.state)
        _save_state(smartClient.state)

    except Exception as e:
        return """<h1>Authorization Error</h1><p>{0}</p><p><a href="/">Start over</a></p>""".format(e)

    return redirect(
        url_for(
            "healthcare_views_bp.healthcare_healthins",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=None,
            message=None))


@healthcare_views_bp.route("/newpatient")
@apply_remote_config
@is_authenticated
def healthcare_newpatient():
    if 'fhir_session_id' in session:
        del session['fhir_session_id']

    return redirect(
        url_for(
            "healthcare_views_bp.healthcare_healthrecord",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            user_id=None,
            message=None))


def _save_state(state):
    sessionId = session.get('fhir_session_id')
    logger.info('Saving FHIR State')
    logger.info(state)
    if sessionId:
        with fhirStoreLock:
            fhirStore[sessionId] = state
    else:
        newSessionId = str(uuid.uuid1())
        session['fhir_session_id'] = newSessionId
        with fhirStoreLock:
            fhirStore[newSessionId] = state


def _get_smart(request):
    smart_config = {
        'app_id': session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_ins_fhir_clientid"],
        'api_base': session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_ins_fhir_api_base"],
        'redirect_uri': request.url_root + "healthcare/smartfhir_callback",
        'scope': 'launch/patient patient/Patient.read patient/MedicationRequest.read patient/Claim.read skip_patient_selection'
    }
    sessionId = session.get('fhir_session_id')
    if sessionId:
        with fhirStoreLock:
            fhirState = fhirStore.get(sessionId)

        if fhirState:
            logger.info('Existing fhir data found!')
            logger.info(fhirState)
            return client.FHIRClient(state=fhirState)
        else:
            logger.info('No FHIR Data Found!')
            return client.FHIRClient(settings=smart_config, save_func=_save_state)

    else:
        logger.info('No FHIR Data Found!')
        return client.FHIRClient(settings=smart_config, save_func=_save_state)
