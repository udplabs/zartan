import os
# Default Settings here are only for testing. We will need to pull down from UDP structure

default_settings = {
    "client_id": os.getenv("OKTA_CLIENT_ID", "0oaqlxnmdpHohO3rV0h7"),
    "client_secret": os.getenv("OKTA_CLIENT_SECRET", "wBDu9TAJtUBywTvp9RIYmhcn-ZfQVsPpb4q-rD3G"),
    "issuer": os.getenv("OKTA_ISSUER", "https://vodkta.oktapreview.com/oauth2/default"),
    "app_config": os.getenv("SITE_APP_CONFIG", "./well-known/default-settings"),
    "okta_org_name": os.getenv("OKTA_ORG_URL", "https://vodkta.oktapreview.com"),
    "redirect_uri": os.getenv("OKTA_OIDC_REDIRECT_URI", "https://fda7d42e54574ac3859bcf5deedf973d.vfs.cloud9.us-east-1.amazonaws.com/authorization-code/callback"),
    "settings": {
        "app_template": os.getenv("APP_TEMPLATE", "finance"),
        "app_base_url": os.getenv("APP_BASE_URL", "https://fda7d42e54574ac3859bcf5deedf973d.vfs.cloud9.us-east-1.amazonaws.com"),
        "app_loginmethod": os.getenv("APP_LOGINMETHOD", "custom-widget"),
        "app_name": os.getenv("APP_NAME", "Commerce Bank"),
        "app_slogan": os.getenv("APP_SLOGAN", "How can we help!"),
        "app_subslogan": os.getenv("APP_SUBSLOGAN", "We’re all in this together."),
        "app_logo": os.getenv("APP_LOGO", "https://www.commercebank.com/-/media/cb/images/masthead/site-logo/commerce-bank-logo-2x.png?sc=1&hash=8507F8EED55D5ADEA33C9D22C91DCF060A727B5B"),
        "app_favicon": os.getenv("APP_FAVICON", "https://www.commercebank.com/-/media/cb/images/global/favicon.ico"),
        "app_banner_img_1": os.getenv("APP_BANNER_1", "https://antlere.com/wp-content/uploads/2019/02/bank-reasons.png"),
        "app_primary_color" : os.getenv("APP_PRIMARY_COLOR", "#006747"),
        "app_secondary_color" : os.getenv("APP_SECONDARY_COLOR", "#78BE20"),
        "app_success_color" : os.getenv("APP_SUCCESS_COLOR", "#0061f2"),
        "app_info_color" : os.getenv("APP_INFO_COLOR", "#0061f2"),
        "app_warning_color" : os.getenv("APP_WARNING_COLOR", "#0061f2"),
        "app_danger_color" : os.getenv("APP_DANGER_COLOR", "#0061f2"),
        "sparkpost_api_key" : os.getenv("SPARKPOST_API_KEY", ""),
        "app_stepup_auth_clientid" : os.getenv("APP_STEPUP_AUTH_CLIENTID", ""),
        "app_stepup_auth_clienturl" : os.getenv("APP_STEPUP_AUTH_CLIENTURL", "")
    },
    "okta_api_token": os.getenv("OKTA_API_TOKEN", "001keV7H5RcridtIWfz5WwAniiJNr2GY7EJZjRdaJ6"),
    "app_secret_key": os.getenv("SECRET_KEY", "bc2cea53-445a-4a67-ae6a-152d6b0aeaa1")
}