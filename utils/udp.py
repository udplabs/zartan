import os
import json
import logging

from config.app_config import default_settings
from config.udp_config import udp_config
from flask import session, request
from functools import wraps
from utils.rest import RestUtil
from utils.okta import OktaUtil

SESSION_INSTANCE_SETTINGS_KEY = "instance_settings"
SESSION_IS_CONFIGURED_KEY = "is_configured_remotely"
SESSION_IS_APITOKEN_VALID_KEY = "is_apitoken_valid"
SESSION_IS_CONFIG_VALID_KEY = "is_config_valid"

logger = logging.getLogger(__name__)

json_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    # "Authorization": "Bearer {0}".format(os.getenv("UDP_SECRET_KEY", ""))
}


def apply_remote_config(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        logger.debug("apply_remote_config()")

        # Rules/Assumptions for remote config with UDP
        # 1) Check if config was set by UDP
        # 2) Attempt UDP config against default_settings
        # 3) Always allow ENV to override UDP i.e. ENV trumps UDP settings
        # logger.debug("is_configured_remotely: {0}".format(is_configured_remotely()))
        if not is_configured_remotely():
            logger.info("Domain is not confgured.  pulling configuration from UDP")
            # Pull remote config here
            # map remote config to default_settings
            domain_parts = get_domain_parts_from_request()
            # logger.debug("domain_parts: {0}".format(domain_parts))
            map_config_to_default_settings(
                get_remote_config(
                    domain_parts["udp_subdomain"],
                    domain_parts["udp_app_name"]))
        else:
            logger.info("Domain is already confgured")

        return f(*args, **kws)
    return decorated_function


def clear_session_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        logger.debug("clear_session_decorator()")

        session[SESSION_IS_CONFIGURED_KEY] = False
        session[SESSION_INSTANCE_SETTINGS_KEY] = default_settings

        return f(*args, **kws)
    return decorated_function


def is_configured_remotely():
    logger.debug("is_configured_remotely()")
    # Always assume false unless explicitly set
    if SESSION_IS_CONFIGURED_KEY not in session:
        session[SESSION_IS_CONFIGURED_KEY] = False

    if SESSION_INSTANCE_SETTINGS_KEY not in session:
        session[SESSION_INSTANCE_SETTINGS_KEY] = default_settings

    return session[SESSION_IS_CONFIGURED_KEY]


def is_apitoken_valid():
    logger.debug("is_apitoken_valid()")
    # Always assume false unless explicitly set
    if SESSION_IS_APITOKEN_VALID_KEY not in session:
        session[SESSION_IS_APITOKEN_VALID_KEY] = False

    return session[SESSION_IS_APITOKEN_VALID_KEY]


def is_config_valid():
    logger.debug("is_config_valid()")
    # Allways assume false unless explicitly set
    if SESSION_IS_CONFIG_VALID_KEY not in session:
        session[SESSION_IS_CONFIG_VALID_KEY] = False

    return session[SESSION_IS_CONFIG_VALID_KEY]


def is_udp_config_valid(config):
    logger.debug("is_udp_config_valid()")
    result = True

    if not config["issuer"]:
        logger.warning("UDP Config: 'issuer' not set")
        result = False

    if not config["client_id"]:
        logger.warning("UDP Config: 'client_id' not set")
        result = False

    if not config["client_secret"]:
        logger.warning("UDP Config: 'client_secret' not set")
        result = False

    return result


def map_config_to_default_settings(config):
    logger.debug("map_config_to_default_settings()")

    if config:
        if "settings" in config:
            logger.debug("Applying Remote Config")
            instance_settings = session[SESSION_INSTANCE_SETTINGS_KEY]

            logger.debug("Before Config: {0}".format(
                json.dumps(instance_settings, indent=4, sort_keys=True)))

            for key, value in instance_settings.items():
                safe_assign_config_item(key, config, instance_settings)

            logger.debug("After Config: {0}".format(
                json.dumps(instance_settings, indent=4, sort_keys=True)))

            session[SESSION_INSTANCE_SETTINGS_KEY] = instance_settings
            session[SESSION_IS_CONFIGURED_KEY] = True
            logger.debug("Remote Config completed!")
        else:
            logger.warning("Remote Config is Invalid: {0}".format(
                json.dumps(config, indent=4, sort_keys=True)))
    else:
        logger.info("No remote config, using default_settings and ENV")


def get_remote_config(udp_subdomain, udp_app_name):
    logger.debug("get_remote_config()")
    remote_config = None

    if(is_udp_config_valid(udp_config)):

        json_headers["Authorization"] = "Bearer {0}".format(get_udp_oauth_access_token(udp_config))

        remote_config_url = "{udp_config_url}/api/configs/{udp_subdomain}/{udp_app_name}".format(
            udp_config_url=os.getenv("UDP_CONFIG_URL", ""),
            udp_subdomain=udp_subdomain,
            udp_app_name=udp_app_name)

        remote_api_token_url = "{udp_config_url}/api/subdomains/{udp_subdomain}".format(
            udp_config_url=os.getenv("UDP_CONFIG_URL", ""),
            udp_subdomain=udp_subdomain)

        if "http" in remote_config_url:
            logger.debug("Pulling remote config from: {0}".format(remote_config_url))

            remote_config = RestUtil.execute_get(remote_config_url, json_headers)
            # logger.debug("config_json: {0}".format(json.dumps(remote_config, indent=4, sort_keys=True)))

        if "http" in remote_api_token_url:
            logger.debug("Pulling remote config from: {0}".format(remote_api_token_url))
            api_token_config = RestUtil.execute_get(remote_api_token_url, json_headers)
            # logger.debug("config_json: {0}".format(json.dumps(api_token_config, indent=4, sort_keys=True)))

            if remote_config:
                if "okta_api_token" in api_token_config:
                    remote_config["okta_api_token"] = api_token_config["okta_api_token"]

        logger.debug("config_json: {0}".format(json.dumps(remote_config, indent=4, sort_keys=True)))
    else:
        logger.warning("Invalid UDP Config, Skipping remote configuration...")

    return remote_config


def get_domain_parts_from_request():
    logger.debug("get_domain_parts_from_request()")

    domain_parts = request.host.split(".")

    if len(domain_parts) >= 3:
        # Assume running in UDP
        udp_subdomain = domain_parts[0]
        udp_app_name = domain_parts[1]
        remaining_domain = ".".join(domain_parts[2:])
    else:
        # Assum local running
        udp_subdomain = "local"
        udp_app_name = "local"
        remaining_domain = "local"

    # ENV always trumps remote config
    udp_subdomain = os.getenv("UDP_SUB_DOMAIN", udp_subdomain)
    udp_app_name = os.getenv("UDP_APP_NAME", udp_app_name)
    remaining_domain = os.getenv("UDP_BASE_DOMAIN", remaining_domain)

    logger.debug("udp_subdomain: {0}".format(udp_subdomain))
    logger.debug("udp_app_name: {0}".format(udp_app_name))

    split_domain_parts = {
        "udp_subdomain": udp_subdomain,
        "udp_app_name": udp_app_name,
        "remaining_domain": remaining_domain
    }

    return split_domain_parts


def safe_assign_config_item(key, source_collection, target_collection):
    if key in source_collection:
        # map sub dicts
        if isinstance(source_collection[key], dict):
            for sub_key, value in source_collection[key].items():
                safe_assign_config_item(sub_key, source_collection[key], target_collection[key])
        else:
            # ENV always overrides source config
            target_collection[key] = os.getenv(key.upper(), source_collection[key])


def clear_session_setting():
    logger.debug("clear_session_setting()")

    session[SESSION_IS_APITOKEN_VALID_KEY] = False
    session[SESSION_IS_CONFIG_VALID_KEY] = False
    session[SESSION_IS_CONFIGURED_KEY] = False
    session[SESSION_INSTANCE_SETTINGS_KEY] = default_settings


def get_app_vertical():
    logger.debug("get_app_vertical()")
    app_vertical_template_name = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_template"]

    logger.debug("app_vertical_template_name: {0}".format(app_vertical_template_name))

    return app_vertical_template_name


def get_udp_oauth_access_token(udp_config):
    logger.debug("get_app_vertical()")
    results = None

    udp_issuer = udp_config["issuer"]
    udp_token_endpoint = "{issuer}/v1/token".format(issuer=udp_issuer)
    udp_oauth_client_id = udp_config["client_id"]
    udp_oauth_client_secret = udp_config["client_secret"]
    basic_auth_encoded = OktaUtil.get_encoded_auth(udp_oauth_client_id, udp_oauth_client_secret)

    oauth2_headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {0}".format(basic_auth_encoded)
    }

    # logger.debug(oauth2_headers)

    url = "{0}?grant_type=client_credentials&scope=secrets:read".format(udp_token_endpoint)

    responseData = RestUtil.execute_post(url, headers=oauth2_headers)
    # logger.debug(responseData)

    if "access_token" in responseData:
        results = responseData["access_token"]
    else:
        logger.warning("Failed to get UDP Service OAuth token: {message}".format(message=responseData))

    return results


def get_udp_ns_fieldname(fieldname):
    parts = get_domain_parts_from_request()
    # Fix for Okta Field Nameing Issue. Okta Custom Fields cannot contain dashes.
    udp_subdomain = parts["udp_subdomain"].replace("-", "_")
    udp_app_name = parts["udp_app_name"]
    field = "{subdomain}_{appname}_{fieldname}".format(subdomain=udp_subdomain, appname=udp_app_name, fieldname=fieldname)

    return field
