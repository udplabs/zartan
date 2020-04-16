import os
import json
import logging

from config import default_settings
from flask import session, request
from functools import wraps
from utils.rest import RestUtil

SESSION_INSTANCE_SETTINGS_KEY = "instance_settings"
SESSION_IS_CONFIGURED_KEY = "is_configured_remotley"
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
        # logger.debug("is_configured_remotley: {0}".format(is_configured_remotley()))
        if not is_configured_remotley():
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


def is_configured_remotley():
    logger.debug("is_configured_remotley()")
    # Allways assume false unless explicitly set
    if SESSION_IS_CONFIGURED_KEY not in session:
        session[SESSION_IS_CONFIGURED_KEY] = False

    if SESSION_INSTANCE_SETTINGS_KEY not in session:
        session[SESSION_INSTANCE_SETTINGS_KEY] = default_settings

    return session[SESSION_IS_CONFIGURED_KEY]


def map_config_to_default_settings(config):
    logger.debug("map_config_to_default_settings()")

    if "settings" in config:
        logger.debug("Applying Remote Config")
        instance_settings = session[SESSION_INSTANCE_SETTINGS_KEY]

        # logger.debug("Before Config: {0}".format(
        #    json.dumps(instance_settings, indent=4, sort_keys=True)))

        for key, value in instance_settings.items():
            safe_assign_config_item(key, config, instance_settings)

        # logger.debug("After Config: {0}".format(
        #    json.dumps(instance_settings, indent=4, sort_keys=True)))

        session[SESSION_INSTANCE_SETTINGS_KEY] = instance_settings
        session[SESSION_IS_CONFIGURED_KEY] = True
        logger.debug("Remote Config completed!")
    else:
        logger.warn("Remote Config is Invalid: {0}".format(
            json.dumps(config, indent=4, sort_keys=True)))


def get_remote_config(udp_subdomain, udp_app_name):
    logger.debug("get_remote_config()")
    remote_config = None
    # TODO: Make the call to UDP Here
    remote_config_url = os.getenv("UDP_CONFIG_URL", "").format(
        udp_subdomain=udp_subdomain,
        udp_app_name=udp_app_name)

    logger.debug("Pulling remote config from: {0}".format(remote_config_url))

    remote_config = RestUtil.execute_get(remote_config_url, json_headers)
    # logger.debug("config_json: {0}".format(json.dumps(remote_config, indent=4, sort_keys=True)))

    return remote_config


def get_domain_parts_from_request():
    logger.debug("get_domain_parts_from_request()")

    domain_parts = request.host.split(".")
    udp_subdomain = domain_parts[0]
    udp_app_name = domain_parts[1]
    remaining_domain = ".".join(domain_parts[2:])

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

    session[SESSION_IS_CONFIGURED_KEY] = False
    session[SESSION_INSTANCE_SETTINGS_KEY] = default_settings


def get_app_vertical():
    app_vertical_template_name = None
    domain_parts = get_domain_parts_from_request()

    if "udp_app_name" in domain_parts:
        app_vertical_template_name = domain_parts["udp_app_name"]

    if app_vertical_template_name == "" or app_vertical_template_name is None:
        app_vertical_template_name = session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["app_template"]

    print("app_vertical_template_name: {0}".format(app_vertical_template_name))

    return app_vertical_template_name

