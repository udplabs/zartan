import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

default_settings = {
    "client_id": os.getenv("OKTA_CLIENT_ID", ""),
    "client_secret": os.getenv("OKTA_CLIENT_SECRET", ""),
    "issuer": os.getenv("OKTA_ISSUER", ""),
    "app_config": os.getenv("SITE_APP_CONFIG", "./well-known/default-settings"),
    "okta_org_name": os.getenv("OKTA_ORG_URL", ""),
    "redirect_uri": os.getenv("OKTA_OIDC_REDIRECT_URI", "http://yoursite/authorization-code/callback"),
    "settings": {
        "app_template": os.getenv("APP_TEMPLATE", "sample"),
        "app_post_login_landing_url": os.getenv("APP_POST_LOGIN_LANDING_URL", "profile"),
        "app_loginmethod": os.getenv("APP_LOGINMETHOD", "standard-widget"),
        "app_name": os.getenv("APP_NAME", "Sample App"),
        "app_slogan": os.getenv("APP_SLOGAN", ""),
        "app_subslogan": os.getenv("APP_SUBSLOGAN", ""),
        "app_logo": os.getenv("APP_LOGO", ""),
        "app_favicon": os.getenv("APP_FAVICON", ""),
        "app_banner_img_1": os.getenv("APP_BANNER_1", ""),
        "app_primary_color": os.getenv("APP_PRIMARY_COLOR", "#0061f2"),
        "app_secondary_color": os.getenv("APP_SECONDARY_COLOR", "#6900c7"),
        "app_success_color": os.getenv("APP_SUCCESS_COLOR", "#00ac69"),
        "app_info_color": os.getenv("APP_INFO_COLOR", "#00cfd5"),
        "app_warning_color": os.getenv("APP_WARNING_COLOR", "#f4a100"),
        "app_danger_color": os.getenv("APP_DANGER_COLOR", "#e81500"),
        "sparkpost_api_key": os.getenv("SPARKPOST_API_KEY", ""),
        "app_stepup_auth_clientid": os.getenv("APP_STEPUP_AUTH_CLIENTID", ""),
        "app_stepup_auth_clienturl": os.getenv("APP_STEPUP_AUTH_CLIENTURL", "")
    },
    "okta_api_token": os.getenv("OKTA_API_TOKEN", ""),
    "app_secret_key": os.getenv("SECRET_KEY", "")
}
