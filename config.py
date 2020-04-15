import os

default_settings = {
    "client_id": os.getenv("OKTA_CLIENT_ID", ""),
    "client_secret": os.getenv("OKTA_CLIENT_SECRET", ""),
    "issuer": os.getenv("OKTA_ISSUER", ""),
    "app_config": os.getenv("SITE_APP_CONFIG", "./well-known/default-settings"),
    "okta_org_name": os.getenv("OKTA_ORG_URL", ""),
    "redirect_uri": os.getenv("OKTA_OIDC_REDIRECT_URI", ""),
    "settings": {
        "app_template": os.getenv("APP_TEMPLATE", "sample"),
        "app_base_url": os.getenv("APP_BASE_URL", ""),
        "app_name": os.getenv("APP_NAME", "Sample App"),
        "app_slogan": os.getenv("APP_SLOGAN", ""),
        "app_subslogan": os.getenv("APP_SUBSLOGAN", ""),
        "app_logo": os.getenv("APP_LOGO", ""),
        "app_favicon": os.getenv("APP_FAVICON", ""),
        "app_banner_img_1": os.getenv("APP_BANNER_1", ""),
        "app_primary_color" : os.getenv("app_primary_color", "#0061f2"),
        "app_secondary_color" : os.getenv("app_secondary_color", "#6900c7"),
        "app_success_color" : os.getenv("app_success_color", "#00ac69"),
        "app_info_color" : os.getenv("app_info_color", "#00cfd5"),
        "app_warning_color" : os.getenv("app_warning_color", "#f4a100"),
        "app_danger_color" : os.getenv("app_danger_color", "#e81500"),
        "app_stepup_auth_clientid" : os.getenv("APP_STEPUP_AUTH_CLIENTID", ""),
        "app_stepup_auth_clienturl" : os.getenv("APP_STEPUP_AUTH_CLIENTURL", "")
    },
    "okta_api_token": os.getenv("OKTA_API_TOKEN", ""),
    "app_secret_key": os.getenv("SECRET_KEY", "")
}
