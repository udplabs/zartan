import logging

# import functions
from flask import session, request, json
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, apply_remote_config
from utils.okta import OktaAdmin, OktaAuth

logger = logging.getLogger(__name__)

# set blueprint
gbac_mfaenrollment_bp = Blueprint('gbac_mfaenrollment_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


def get_enrolled_factors(user_id):
    print("get_enrolled_factors()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    enrolled_factors = okta_admin.list_enrolled_factors(user_id)

    factors = []

    for f in enrolled_factors:
        logger.debug(f["factorType"])
        factor = {}
        factor["id"] = f["id"]
        factor["type"] = f["factorType"]
        factor["provider"] = f["provider"]
        factor["vendor"] = f["vendorName"]

        switcher = {
            'token:software:totp': totp,
            'push': push,
            'webauthn': webauthn,
            'sms': sms,
            'call': call,
            'question': question
        }

        logger.debug(f["status"] )
        if f["status"] == "ACTIVE" :
            myfactor = switcher.get(f["factorType"])
        else:
            myfactor = None

        if myfactor is not None:
            factor = myfactor(factor, f)
            factors.append(factor)

    return factors


def totp(factor, f):
    logger.debug("TOTP")
    provider = f["provider"]
    if (provider == "GOOGLE"):
        factor["name"] = "Google Authenticator"
        factor["profile"] = f["profile"]["credentialId"]
        factor["sortOrder"] = 20
    else:
        factor = None
    return factor


def push(factor, f):
    logger.debug("Push")
    factor["name"] = "Okta Verify"
    if "status" in f:
        factor["profile"] = f["status"]
    else:
        factor["profile"] = "Not Defined"

    factor["sortOrder"] = 10
    return factor


def webauthn(factor, f):
    logger.debug("WebAuth")
    logger.debug(f)
    factor["name"] = "WebAuthn"
    factor["profile"] = f["profile"]["authenticatorName"]
    #factor["profile"] = "WebAuthn"
    factor["sortOrder"] = 15
    return factor



def sms(factor, f):
    logger.debug("SMS")
    factor["name"] = "SMS"
    factor["profile"] = f["profile"]["phoneNumber"]
    factor["sortOrder"] = 30
    return factor


def call(factor, f):
    logger.debug("Call")
    factor["name"] = "Voice Call"
    factor["profile"] = f["profile"]["phoneNumber"]
    factor["sortOrder"] = 40
    return factor


def question(factor, f):
    logger.debug("Question")
    factor["name"] = "Security Question"
    factor["profile"] = f["profile"]["questionText"]
    factor["sortOrder"] = 50
    return factor

@gbac_mfaenrollment_bp.route("/get_available_factors/<user_id>", methods=["GET"])
@apply_remote_config
def get_available_factors(user_id):
    print("get_available_factors()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    available_factors = okta_admin.list_available_factors(user_id)
    factors = []
    logging.debug(available_factors)
    for f in available_factors:
        if f["status"] == "NOT_SETUP" or f["factorType"] == "webauthn":
            factorType = f["factorType"]
            provider = f["provider"]

            try:
                phone_number = f["_embedded"]["phones"][0]["profile"]["phoneNumber"]
            except Exception:
                phone_number = None

            logging.debug(get_factor_name(factorType, provider) + provider)

            factor = {
                "factorType": factorType,
                "provider": provider,
                "phoneNumber": phone_number,
                "name": get_factor_name(factorType, provider)
            }

            if (provider == "SYMANTEC"):
                # do nothing
                continue
            else:
                factors.append(factor)

    return json.dumps(factors)


@gbac_mfaenrollment_bp.route('/get_available_factors_by_state/<state_token>', methods=["POST"])
@apply_remote_config
def get_available_factors_by_state(state_token):
    """ Get all factors available by State Token """
    print("get_available_factors_by_state()")

    okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])

    transaction_state = okta_auth.get_transaction_state(state_token)

    print("transaction_state: {0}".format(json.dumps(transaction_state, indent=4, sort_keys=True)))

    # available_factors = okta_admin.list_available_factors(transaction_state["_embedded"]["user"]["id"])

    return json.dumps(transaction_state)


@gbac_mfaenrollment_bp.route("/enroll_push", methods=["POST"])
@apply_remote_config
def enroll_push():
    print("enroll_push()")

    body = request.get_json()
    factor_type = body["factor_type"]
    provider = body["provider"]

    if "state_token" in body:
        # this is an enrollment during the authN process
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        state_token = body["state_token"]
        response = okta_auth.enroll_push(state_token, factor_type, provider)
    else:
        user_id = body["user_id"]
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        response = okta_admin.enroll_push(user_id, factor_type, provider)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/poll_for_push_enrollment", methods=["POST"])
@apply_remote_config
def poll_for_push_enrollment():
    print("poll_for_push_enrollment()")

    body = request.get_json()
    factor_id = body["factor_id"]

    if "state_token" in body:
        state_token = body["state_token"]
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        response = okta_auth.poll_for_enrollment_push(factor_id, state_token)
    else:
        user_id = body["user_id"]
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        response = okta_admin.poll_for_enrollment_push(user_id, factor_id)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/enroll_totp", methods=["POST"])
@apply_remote_config
def enroll_totp():
    print("enroll_totp()")

    body = request.get_json()
    factor_type = body["factor_type"]
    provider = body["provider"]

    if "stateToken" in body:
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        state_token = body["state_token"]
        response = okta_auth.enroll_totp(state_token, factor_type, provider)
    else:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        user_id = body["user_id"]
        response = okta_admin.enroll_totp(user_id, factor_type, provider)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/enroll_webauthn", methods=["POST"])
@apply_remote_config
def enroll_webauthn():
    print("enroll_webauthn()")

    body = request.get_json()
    factor_type = body["factor_type"]
    provider = body["provider"]

    if "stateToken" in body:
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        state_token = body["state_token"]
        response = okta_auth.enroll_webauthn(state_token, factor_type, provider)
    else:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        user_id = body["user_id"]
        response = okta_admin.enroll_webauthn(user_id, factor_type, provider)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/enroll_sms_voice", methods=["POST"])
@apply_remote_config
def enroll_sms_voice():
    print("enroll_sms_voice()")

    body = request.get_json()
    factor_type = body["factor_type"]
    provider = body["provider"]
    phone_number = body["phone_number"]

    if "state_token" in body:
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        state_token = body["state_token"]
        response = okta_auth.enroll_sms_voice(state_token, factor_type, provider, phone_number)
    else:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        user_id = body["user_id"]
        response = okta_admin.enroll_sms_voice(user_id, factor_type, provider, phone_number)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/enroll_question", methods=["POST"])
@apply_remote_config
def enroll_question():
    print("enroll_question()")

    body = request.get_json()
    factor_type = body["factor_type"]
    provider = body["provider"]
    question = body["question"]
    answer = body["answer"]

    if "state_token" in body:
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        state_token = body["state_token"]
        response = okta_auth.enroll_question(state_token, factor_type, provider, question, answer)
    else:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        user_id = body["user_id"]
        response = okta_admin.enroll_question(user_id, factor_type, provider, question, answer)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/list_available_questions", methods=["POST"])
@apply_remote_config
def list_available_questions():
    print("list_available_questions()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    body = request.get_json()
    user_id = body["user_id"]
    response = okta_admin.list_available_questions(user_id)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/activate_totp", methods=["POST"])
@apply_remote_config
def activate_totp():
    print("activate_totp()")

    body = request.get_json()
    factor_id = body["factor_id"]
    pass_code = body["pass_code"]

    if "state_token" in body:
        okta_auth = OktaAuth(session[SESSION_INSTANCE_SETTINGS_KEY])
        state_token = body["state_token"]
        response = okta_auth.activate_totp(factor_id, state_token, pass_code)
    else:
        okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
        user_id = body["user_id"]
        response = okta_admin.activate_totp(user_id, factor_id, pass_code)

    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/activate_webauthn", methods=["POST"])
@apply_remote_config
def activate_webauthn():
    print("activate_webauthn()")

    body = request.get_json()
    factor_id = body["factor_id"]
    user_id = body["user_id"]
    attestation = body["attestation"]
    clientData = body["clientData"]

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    response = okta_admin.activate_webauthn(user_id, factor_id, attestation, clientData)
    print(response)
    return json.dumps(response)


@gbac_mfaenrollment_bp.route("/reset_factor/<user_id>/<factor_id>", methods=["GET"])
@apply_remote_config
def reset_factor(user_id, factor_id):
    print("reset_factor()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    response = okta_admin.delete_factor(user_id, factor_id)

    return json.dumps(response)


def get_factor_name(factorType, provider):
    factor_name = factorType

    if (factorType == "token:software:totp"):
        if (provider == "GOOGLE"):
            factor_name = "Google Authenticator"
    elif (factorType == "push"):
        factor_name = "Okta Verify"
    elif (factorType == "sms"):
        factor_name = "SMS"
    elif (factorType == "call"):
        factor_name = "Voice Call"
    elif (factorType == "question"):
        factor_name = "Security Question"

    return factor_name
