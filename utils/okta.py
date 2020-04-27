import base64
import json
import logging

from utils.rest import RestUtil


class OktaAuth:

    okta_config = None
    logger = logging.getLogger(__name__)

    def __init__(self, okta_config):
        self.logger.debug("OktaAuth init()")
        if okta_config:
            self.okta_config = okta_config
            # print("self.okta_config: {0}".format(self.okta_config))
        else:
            raise Exception("Requires okta_config")

    def authenticate(self, username, password, additional_options=None, headers=None):
        print("OktaAuth.authenticate()")
        url = "{host}/api/v1/authn".format(host=self.okta_config["okta_org_name"])
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        body = {
            "username": username,
            "password": password,
        }

        if additional_options:
            RestUtil.map_attribute("audience", additional_options, body)
            RestUtil.map_attribute("relayState", additional_options, body)
            RestUtil.map_attribute("options", additional_options, body)
            RestUtil.map_attribute("context", additional_options, body)
            RestUtil.map_attribute("token", additional_options, body)

        return RestUtil.execute_post(url, body, okta_headers)

    def authenticate_with_activation_token(self, token, headers=None):
        print("OktaAuth.authenticate_with_activation_token()")
        url = "{host}/api/v1/authn".format(host=self.okta_config["okta_org_name"])
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        body = {
            "token": token
        }

        return RestUtil.execute_post(url, body, okta_headers)

    def get_transaction_state(self, token, headers=None):
        print("OktaAuth.authenticate_with_activation_token()")
        url = "{host}/api/v1/authn".format(host=self.okta_config["okta_org_name"])
        okta_headers = OktaUtil.get_default_okta_headers(self.okta_config)

        body = {
            "stateToken": token
        }

        return RestUtil.execute_post(url, body, okta_headers)

    def reset_password_with_state_token(self, token, password, headers=None):
        print("OktaAuth.reset_password_with_state_token()")
        url = "{host}/api/v1/authn/credentials/reset_password".format(host=self.okta_config["okta_org_name"])
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        body = {
            "stateToken": token,
            "newPassword": password
        }

        return RestUtil.execute_post(url, body, okta_headers)

    def create_oauth_authorize_url(self, response_type, state, auth_options):
        print("OktaAuth.create_oauth_authorize_url()")

        url = (
            "{issuer}/v1/authorize?"
            "response_type={response_type}&"
            "client_id={clint_id}&"
            "redirect_uri={redirect_uri}&"
            "state={state}"
        ).format(
            issuer=self.okta_config["issuer"],
            clint_id=self.okta_config["client_id"],
            redirect_uri=self.okta_config["redirect_uri"],
            state=state,
            response_type=response_type
        )

        if auth_options:
            for key in auth_options:
                url = "{url}&{key}={value}".format(url=url, key=key, value=auth_options[key])

        return url

    def get_oauth_token(self, code, grant_type, auth_options=None, headers=None):
        print("OktaAuth.get_oauth_token()")
        okta_headers = OktaUtil.get_oauth_okta_headers(headers)

        url = (
            "{issuer}/v1/token?"
            "grant_type={grant_type}&"
            "code={code}&"
            "redirect_uri={redirect_uri}"
        ).format(
            issuer=self.okta_config["issuer"],
            code=code,
            redirect_uri=self.okta_config["redirect_uri"],
            grant_type=grant_type
        )

        body = {
            "authorization_code": code
        }

        if auth_options:
            for key in auth_options:
                url = "{url}&{key}={value}".format(url=url, key=key, value=auth_options[key])

        return RestUtil.execute_post(url, body, okta_headers)

    def introspect(self, token, headers=None):
        print("OktaAuth.introspect()")
        okta_headers = OktaUtil.get_oauth_okta_headers(headers, self.okta_config["client_id"], self.okta_config["client_secret"])

        url = "{issuer}/v1/introspect?token={token}".format(
            issuer=self.okta_config["issuer"],
            token=token)
        body = {}

        return RestUtil.execute_post(url, body, okta_headers)

    def introspect_mfa(self, token, client_id):
        self.logger.debug("OktaAuth.introspect_mfa()")
        okta_headers = OktaUtil.get_introspect_mfa_okta_headers()
        url = "{baseurl}/oauth2/v1/introspect".format(
            baseurl=self.okta_config["okta_org_name"]
        )
        body = "&token={token}&client_id={client_id}&token_type_hint=id_token".format(
            token=token,
            client_id=client_id
        )
        return RestUtil.execute_post(url=url, body=body, headers=okta_headers)

    def userinfo(self, token, headers=None):
        self.logger.debug("OktaAuth.userinfo()")
        okta_headers = OktaUtil.get_oauth_okta_bearer_token_headers(headers, token)
        # self.logger.debug("okta_headers: {0}".format(okta_headers))
        url = "{issuer}/v1/userinfo".format(issuer=self.okta_config["issuer"])
        body = {}
        return RestUtil.execute_post(url, body, okta_headers)

    """
    MFA verification methods
    """
    # used by Okta Verify Push, this starts the MFA transaction
    def send_push(self, factor_id, state_token, headers=None):
        print("send_push()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/verify".format(self.okta_config["okta_org_name"], factor_id)
        body = {
            "stateToken": state_token
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # this is the Okta Verify Push polling method
    def poll_for_push(self, factor_id, state_token, headers=None):
        print("poll_for_push()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/verify".format(self.okta_config["okta_org_name"], factor_id)
        body = {
            "stateToken": state_token
        }
        return RestUtil.execute_post(url, body, okta_headers)

    def resend_push(self, factor_id, state_token, headers=None):
        print("resend_push()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/verify/resend".format(self.okta_config["okta_org_name"], factor_id)
        body = {
            "stateToken": state_token
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # used by SMS, voice, Google Authenticator and Okta Verify OTP factors
    def verify_totp(self, factor_id, state_token, pass_code=None, headers=None):
        print("verify_totp()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/verify".format(self.okta_config["okta_org_name"], factor_id)
        body = {
            "stateToken": state_token,
            "passCode": pass_code
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # used for Security Question factor
    def verify_answer(self, factor_id, state_token, answer, headers=None):
        print("verify_answer()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/verify".format(self.okta_config["okta_org_name"], factor_id)
        body = {
            "stateToken": state_token,
            "answer": answer
        }

        return RestUtil.execute_post(url, body, okta_headers)

    """
    end MFA verification methods
    """

    """
    MFA enrollment methods
    """
    # Okta Verify Push
    def enroll_push(self, state_token, factor_type, provider, headers=None):
        print("enroll_push()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors".format(self.okta_config["okta_org_name"])
        body = {
            "stateToken": state_token,
            "factorType": factor_type,
            "provider": provider
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # this is the Okta Verify Push polling method
    def poll_for_enrollment_push(self, factor_id, state_token, headers=None):
        print("poll_for_enrollment_push()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/lifecycle/activate/poll".format(
            self.okta_config["okta_org_name"],
            factor_id
        )
        body = {
            "stateToken": state_token
        }
        return RestUtil.execute_post(url, body, okta_headers)

    # this is the Okta Verify Push activation method
    def activate_push(self, factor_id, state_token, headers=None):
        print("activate_push()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/lifecycle/activate".format(
            self.okta_config["okta_org_name"],
            factor_id
        )
        body = {
            "stateToken": state_token
        }
        return RestUtil.execute_post(url, body, okta_headers)

    # Okta Verify OTP and Google Authenticator
    def enroll_totp(self, state_token, factor_type, provider, headers=None):
        print("enroll_totp()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors".format(self.okta_config["okta_org_name"])
        body = {
            "stateToken": state_token,
            "factorType": factor_type,
            "provider": provider
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # SMS and voice call
    def enroll_sms_voice(self, state_token, factor_type, provider, phone_number, headers=None):
        print("enroll_sms_voice()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors".format(self.okta_config["okta_org_name"])
        body = {
            "stateToken": state_token,
            "factorType": factor_type,
            "provider": provider,
            "profile": {
                "phoneNumber": phone_number
            }
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # security question
    def enroll_question(self, state_token, factor_type, provider, question, answer, headers=None):
        print("enroll_question()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors".format(self.okta_config["okta_org_name"])
        body = {
            "stateToken": state_token,
            "factorType": factor_type,
            "provider": provider,
            "profile": {
                "question": question,
                "answer": answer
            }
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # this is for Google Authenticator, SMS, and Voice factors
    def activate_totp(self, factor_id, state_token, pass_code, headers=None):
        print("enroll_totp()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/authn/factors/{1}/lifecycle/activate".format(
            self.okta_config["okta_org_name"],
            factor_id
        )
        body = {
            "stateToken": state_token,
            "passCode": pass_code
        }

        return RestUtil.execute_post(url, body, okta_headers)

    """
    MFA enrollment methods
    """


class OktaAdmin:

    okta_config = None

    def __init__(self, okta_config):
        print("OktaAdmin init()")
        if okta_config:
            self.okta_config = okta_config
        else:
            raise Exception("Requires okta_config")

    def get_user(self, user_id):
        print("OktaAdmin.get_user(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users/{user_id}".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id)

        return RestUtil.execute_get(url, okta_headers)

    def get_user_groups(self, user_id):
        print("OktaAdmin.get_user_groups(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users/{user_id}/groups".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id)

        return RestUtil.execute_get(url, okta_headers)

    def create_user(self, user, activate_user=False):
        print("OktaAdmin.create_user(user)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users?activate={activate_user}".format(
            base_url=self.okta_config["okta_org_name"],
            activate_user=activate_user)

        return RestUtil.execute_post(url, user, okta_headers)

    def update_user(self, user_id, user):
        print("OktaAdmin.update_user()")
        print("User profile: {0}".format(json.dumps(user)))
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users/{user_id}".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id)

        return RestUtil.execute_post(url, user, okta_headers)

    def activate_user(self, user_id, send_email=True):
        print("OktaAdmin.activate_user(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users/{user_id}/lifecycle/activate/?sendEmail={send_email}".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id,
            send_email=str(send_email).lower())
        body = {}

        return RestUtil.execute_post(url, body, okta_headers)

    def suspend_user(self, user_id):
        print("OktaAdmin.suspend_user(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users/{user_id}/lifecycle/suspend".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id)
        print(user_id)
        body = {}

        return RestUtil.execute_post(url, body, okta_headers)

    def unsuspend_user(self, user_id):
        print("OktaAdmin.unsuspend_user(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users/{user_id}/lifecycle/unsuspend".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id)
        body = {}

        return RestUtil.execute_post(url, body, okta_headers)

    def reset_password_for_user(self, user_id):
        print("OktaAdmin.unsuspend_user(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users/{user_id}/lifecycle/reset_password".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id)
        body = {}

        return RestUtil.execute_post(url, body, okta_headers)

    def get_groups_by_name(self, name):
        print("OktaAdmin.get_groups_by_name(name)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/groups?q={name}".format(
            base_url=self.okta_config["okta_org_name"],
            name=name)

        return RestUtil.execute_get(url, okta_headers)

    def get_group(self, id):
        print("OktaAdmin.get_group(id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/groups/{id}".format(
            base_url=self.okta_config["okta_org_name"],
            id=id)

        return RestUtil.execute_get(url, okta_headers)

    def get_user_list_by_group_id(self, id):
        print("OktaAdmin.get_user_list_by_group_id(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/groups/{id}/users".format(
            base_url=self.okta_config["okta_org_name"],
            id=id)

        return RestUtil.execute_get(url, okta_headers)

    def get_user_list_by_search(self, search):
        # /api/v1/users?search=profile.department eq "Engineering"
        print("OktaAdmin.get_user_list_by_search(search)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/users?search={search}".format(
            base_url=self.okta_config["okta_org_name"],
            search=search)

        return RestUtil.execute_get(url, okta_headers)

    def assign_user_to_group(self, group_id, user_id):
        print("OktaAdmin.assign_user_to_group(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1//groups/{group_id}/users/{user_id}".format(
            base_url=self.okta_config["okta_org_name"],
            group_id=group_id,
            user_id=user_id)
        body = {}

        return RestUtil.execute_put(url, body, okta_headers)

    def get_applications_by_user_id(self, user_id):
        print("OktaAdmin.get_applications_by_user_id(user_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/apps/?filter=user.id+eq+\"{user_id}\"".format(
            base_url=self.okta_config["okta_org_name"],
            user_id=user_id)

        return RestUtil.execute_get(url, okta_headers)

    def get_user_application_by_current_client_id(self, user_id):
        print("OktaAdmin.get_user_application_by_current_client_id()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{base_url}/api/v1/apps/{app_id}/users/{user_id}".format(
            base_url=self.okta_config["okta_org_name"],
            app_id=self.okta_config["client_id"],
            user_id=user_id)

        return RestUtil.execute_get(url, okta_headers)

    def update_application_user_profile(self, user_id, app_user_profile):
        print("OktaAdmin.update_application_user_profile()")
        print("App user profile: {0}".format(json.dumps(app_user_profile)))

        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/apps/{app_id}/users/{user_id}".format(
            base_url=self.okta_config["okta_org_name"],
            app_id=self.okta_config["client_id"],
            user_id=user_id)

        body = {
            "profile": app_user_profile["profile"]
        }

        return RestUtil.execute_post(url, body, okta_headers)

    def close_session(self, session_id):
        print("OktaAdmin.close_session(session_id)")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)
        url = "{base_url}/api/v1/sessions/{session_id}".format(
            base_url=self.okta_config["okta_org_name"],
            session_id=session_id)

        print("url: {0}".format(url))

        body = {}

        return RestUtil.execute_delete(url, body, okta_headers)

    """
    MFA enrollment methods
    These are for enrollment outside of the authentication process
    """

    # Okta Verify Push
    def enroll_push(self, user_id, factor_type, provider, headers=None):
        print("enroll_push()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors".format(
            self.okta_config["okta_org_name"],
            user_id
        )
        body = {
            "factorType": factor_type,
            "provider": provider
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # this is the Okta Verify Push polling method
    def poll_for_enrollment_push(self, user_id, factor_id, headers=None):
        print("poll_for_enrollment_push()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors/{2}/lifecycle/activate/poll".format(
            self.okta_config["okta_org_name"],
            user_id,
            factor_id
        )
        body = {}

        return RestUtil.execute_post(url, body, okta_headers)

    def resend_push(self, user_id, factor_id, headers=None):
        print("resend_push()")
        okta_headers = OktaUtil.get_default_okta_headers(headers)

        url = "{0}/api/v1/users/{1}/factors/{2}/lifecycle/activate".format(
            self.okta_config["okta_org_name"],
            user_id,
            factor_id
        )
        body = {}

        return RestUtil.execute_post(url, body, okta_headers)

    # Okta Verify OTP and Google Authenticator
    def enroll_totp(self, user_id, factor_type, provider, headers=None):
        print("enroll_totp()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors".format(
            self.okta_config["okta_org_name"],
            user_id
        )
        body = {
            "factorType": factor_type,
            "provider": provider
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # Okta Verify Enroll Security Question
    def enroll_securityquestion(self, user_id, question, answer, headers=None):
        print("enroll_securityquestion()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors".format(
            self.okta_config["okta_org_name"],
            user_id
        )
        body = {
            "factorType": "question",
            "provider": "OKTA",
            "profile":
                {
                    "question": question,
                    "answer": answer
                }
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # Okta Verify Enroll Hard Token
    def enroll_hardtoken(self, user_id, factorProfileId, sharedSecret, headers=None):
        print("enroll_hardtoken()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors?activate=true".format(
            self.okta_config["okta_org_name"],
            user_id
        )
        body = {
            "factorType": "token:hotp",
            "provider": "CUSTOM",
            "factorProfileId": factorProfileId,
            "profile":
                {
                    "sharedSecret": sharedSecret
                }
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # Okta Delete Factor
    def delete_factor(self, user_id, factor_id, headers=None):
        print("delete_securityquestion()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors/{2}".format(
            self.okta_config["okta_org_name"],
            user_id,
            factor_id
        )

        return RestUtil.execute_delete(url=url, headers=okta_headers)

    # SMS and voice call
    def enroll_sms_voice(self, user_id, factor_type, provider, phone_number, headers=None):
        print("enroll_sms_voice()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors?updatePhone=true".format(
            self.okta_config["okta_org_name"],
            user_id
        )
        body = {
            "factorType": factor_type,
            "provider": provider,
            "profile": {
                "phoneNumber": phone_number
            }
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # used by SMS, voice, Google Authenticator and Okta Verify OTP factors
    def activate_totp(self, user_id, factor_id, pass_code, headers=None):
        print("verify_totp()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors/{2}/lifecycle/activate".format(
            self.okta_config["okta_org_name"],
            user_id,
            factor_id
        )
        body = {
            "passCode": pass_code
        }

        return RestUtil.execute_post(url, body, okta_headers)

    # security question
    def enroll_question(self, user_id, factor_type, provider, question, answer, headers=None):
        print("enroll_question()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors".format(
            self.okta_config["okta_org_name"],
            user_id
        )
        body = {
            "factorType": factor_type,
            "provider": provider,
            "profile": {
                "question": question,
                "answer": answer
            }
        }

        return RestUtil.execute_post(url, body, okta_headers)

    def list_enrolled_factors(self, user_id):
        print("list_enrolled_factors()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors".format(
            self.okta_config["okta_org_name"],
            user_id
        )

        return RestUtil.execute_get(url, okta_headers)

    def list_available_factors(self, user_id):
        print("list_available_factors()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors/catalog".format(
            self.okta_config["okta_org_name"],
            user_id
        )

        return RestUtil.execute_get(url, okta_headers)

    def list_available_questions(self, user_id):
        print("list_available_questions()")
        okta_headers = OktaUtil.get_protected_okta_headers(self.okta_config)

        url = "{0}/api/v1/users/{1}/factors/questions".format(
            self.okta_config["okta_org_name"],
            user_id
        )

        return RestUtil.execute_get(url, okta_headers)


class OktaUtil:

    @staticmethod
    def get_default_okta_headers(headers):
        okta_default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        return okta_default_headers

    @staticmethod
    def get_introspect_mfa_okta_headers():
        okta_default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        return okta_default_headers

    @staticmethod
    def get_protected_okta_headers(okta_config):
        okta_api_token = okta_config["okta_api_token"]
        okta_protected_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "SSWS {0}".format(okta_api_token)
        }

        return okta_protected_headers

    @staticmethod
    def get_oauth_okta_headers(headers, client_id=None, client_secret=None):
        okta_oauth_headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        if client_id and client_secret:
            okta_oauth_headers["Authorization"] = "Basic {0}".format(OktaUtil.get_encoded_auth(client_id, client_secret))

        return okta_oauth_headers

    @staticmethod
    def get_oauth_okta_bearer_token_headers(headers, token):
        okta_oauth_headers = {"Authorization": "Bearer {0}".format(token)}

        return okta_oauth_headers

    @staticmethod
    def get_encoded_auth(client_id, client_secret):
        auth_raw = "{client_id}:{client_secret}".format(
            client_id=client_id,
            client_secret=client_secret
        )

        encoded_auth = base64.b64encode(bytes(auth_raw, 'UTF-8')).decode("UTF-8")

        return encoded_auth


class TokenUtil:
    ID_TOKEN_KEY = "idToken"
    ACCESS_TOKEN_KEY = "accessToken"
    OKTA_TOKEN_COOKIE_KEY = "okta-token-storage"

    logger = logging.getLogger(__name__)

    @staticmethod
    def get_single_claim_from_token(token, claim_name):

        ("get_single_claim_from_token")
        claims = TokenUtil.get_claims_from_token(token)
        if claim_name in claims:
            TokenUtil.logger.debug("claim found")
            found_claim = claims[claim_name]
        else:
            TokenUtil.logger.debug("claim not found")
            found_claim = ""
        return found_claim

    @staticmethod
    def get_claims_from_token(token):
        TokenUtil.logger.debug("get_claims_from_token(token)")
        claims = None

        if token:
            jwt = token.encode("utf-8")

            token_payload = jwt.decode().split(".")[1]

            claims_string = TokenUtil.decode_base64(token_payload)

            claims = json.loads(claims_string)

        return claims

    @staticmethod
    def decode_base64(data):
        missing_padding = len(data) % 4
        if missing_padding > 0:
            data += "=" * (4 - missing_padding)
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def create_okta_token_cookie(access_token, id_token):
        TokenUtil.logger.debug("create_okta_token_cookie()")
        okta_token_cookie = {}

        access_token_claims = TokenUtil.get_claims_from_token(access_token)
        id_token_claims = TokenUtil.get_claims_from_token(id_token)

        okta_token_cookie[TokenUtil.ACCESS_TOKEN_KEY] = {
            TokenUtil.ACCESS_TOKEN_KEY: access_token,
            "expiresAt": access_token_claims["exp"],
            "tokenType": "Bearer",
            "scopes": access_token_claims["scp"],
            "authorizeUrl": "{iss}/v1/authorize".format(iss=access_token_claims["iss"]),
            "userinfoUrl": "{iss}/v1/userinfo".format(iss=access_token_claims["iss"])
        }

        okta_token_cookie[TokenUtil.ID_TOKEN_KEY] = {
            TokenUtil.ID_TOKEN_KEY: id_token,
            "claims": id_token_claims,
            "expiresAt": id_token_claims["exp"],
            "scopes": access_token_claims["scp"],  # Grab scopes from the access token
            "authorizeUrl": "{iss}/v1/authorize".format(iss=id_token_claims["iss"]),
            "issuer": id_token_claims["iss"],
            "clientId": access_token_claims["cid"]  # Grab ClientId from access token
        }

        return okta_token_cookie

    @staticmethod
    def create_encoded_okta_token_cookie(access_token, id_token):
        TokenUtil.logger.debug("create_encoded_okta_token_cookie()")
        string_token = json.dumps(TokenUtil.create_okta_token_cookie(access_token, id_token))
        # encoded_string_token = quote(string_token)
        cleaned_string = string_token.replace(" ", "%20").replace("\"", "%22").replace(",", "%2C")
        return cleaned_string

    @staticmethod
    def parse_encoded_okta_token_cookie(encoded_okta_token_cookie):
        TokenUtil.logger.debug("parse_urlencoded_okta_token_cookie()")
        result = None
        if encoded_okta_token_cookie:
            # TokenUtil.logger.debug("encoded_okta_token_cookie: {0}".format(encoded_okta_token_cookie))
            result = encoded_okta_token_cookie.replace("%20", " ").replace("%22", "\"").replace("%2C", ",")
            # result = unquote(result)
            # TokenUtil.logger.debug("result: {0}".format(result))
        return result

    @staticmethod
    def get_access_token(collection):
        # TokenUtil.logger.debug("get_access_token()")
        return TokenUtil.get_jwt_token(collection, TokenUtil.ACCESS_TOKEN_KEY)

    @staticmethod
    def get_id_token(collection):
        # TokenUtil.logger.debug("get_id_token()")
        return TokenUtil.get_jwt_token(collection, TokenUtil.ID_TOKEN_KEY)

    @staticmethod
    def get_jwt_token(collection, key):
        # TokenUtil.logger.debug("get_jwt_token('{0}')".format(key))
        token = None
        if TokenUtil.OKTA_TOKEN_COOKIE_KEY in collection:
            if collection[TokenUtil.OKTA_TOKEN_COOKIE_KEY]:
                token_cookie = TokenUtil.parse_encoded_okta_token_cookie(
                    collection[TokenUtil.OKTA_TOKEN_COOKIE_KEY])
                # TokenUtil.logger.debug("token_cookie: {0}".format(token_cookie))
                parsed_token_cookie = json.loads(token_cookie)
                if key in parsed_token_cookie:
                    token = parsed_token_cookie[key][key]

        return token

    @staticmethod
    def is_valid_remote(token, app_config):
        TokenUtil.logger.debug("is_valid_remote")
        result = False

        if token:
            okta_auth = OktaAuth(app_config)
            introspect_result = okta_auth.introspect(token)

            if introspect_result:
                if "active" in introspect_result:
                    result = introspect_result["active"]

        return result
