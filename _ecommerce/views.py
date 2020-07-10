import logging
import requests

# import functions
from flask import render_template, session, request
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from utils.okta import TokenUtil, OktaAdmin

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo
from GlobalBehaviorandComponents.mfaenrollment import get_enrolled_factors

logger = logging.getLogger(__name__)

# set blueprint
ecommerce_views_bp = Blueprint('ecommerce_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@ecommerce_views_bp.route("/profile")
@is_authenticated
def ecommerce_profile():
    logger.debug("ecommerce_profile()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_info = get_userinfo()
    user_info2 = okta_admin.get_user(user_info["sub"])
    factors = get_enrolled_factors(user_info["sub"])
    return render_template(
        "ecommerce/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        user_info=user_info,
        user_info2=user_info2,
        factors=factors,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])


# Account Page
@ecommerce_views_bp.route("/account")
@is_authenticated
def ecommerce_account():
    logger.debug("ecommerce_account()")
    return render_template("ecommerce/account.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY], _scheme="https")


@ecommerce_views_bp.route("/shop")
def ecommerce_shop():
    logger.debug("ecommerce_shop()")
    products = requests.get(url="https://dz-static-test.s3.amazonaws.com/dell.json")

    return render_template(
        "ecommerce/shop.html",
        templatename=get_app_vertical(),
        products=products.json(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        user_info=get_userinfo(),
        _scheme="https")


@ecommerce_views_bp.route("/product/<product_id>")
def ecommerce_product(product_id):
    logger.debug("ecommerce_product()")
    products = requests.get(url="https://dz-static-test.s3.amazonaws.com/dell.json")

    return render_template(
        "ecommerce/product.html",
        templatename=get_app_vertical(),
        products=products.json(),
        user_info=get_userinfo(),
        productid=product_id,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme="https")


# checkout Page
@ecommerce_views_bp.route("/checkout")
@is_authenticated
def ecommerce_checkout():
    logger.debug("ecommerce_checkout()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])

    return render_template("ecommerce/checkout.html", user=user, user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY], _scheme="https")


# Apply Credit Page
@ecommerce_views_bp.route("/apply")
@is_authenticated
def ecommerce_apply():
    logger.debug("ecommerce_apply()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])

    return render_template("ecommerce/apply.html", user=user, user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY], _scheme="https")


# Order Page
@ecommerce_views_bp.route("/order")
@is_authenticated
def ecommerce_order():
    logger.debug("ecommerce_order()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user = okta_admin.get_user(user_info["sub"])

    return render_template("ecommerce/order.html", user=user, user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY], _scheme="https")


# updateuser Page
@ecommerce_views_bp.route("/updateuser")
@is_authenticated
def ecommerce_updateuser():
    logger.debug("ecommerce_updateuser()")
    user_info = get_userinfo()
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    logger.debug(request)

    firstname = request.args["firstName"]
    lastname = request.args["lastName"]
    email = request.args["email"]
    primaryPhone = request.args["phone"]
    mobilePhone = request.args["phone"]
    streetAddress = request.args["streetAddress"]
    city = request.args["city"]
    state = request.args["state"]
    zipCode = request.args["zipCode"]
    countryCode = request.args["countryCode"]

    user_data = {
        "profile": {
            "firstName": firstname,
            "lastName": lastname,
            "email": email,
            "primaryPhone": primaryPhone,
            "mobilePhone": mobilePhone,
            "streetAddress": streetAddress,
            "city": city,
            "state": state,
            "zipCode": zipCode,
            "countryCode": countryCode
        }
    }
    logger.debug(user_data)
    response = okta_admin.update_user(user_id=user_info["sub"], user=user_data)
    logger.debug(response)
    return response


# See if credit app exists
@ecommerce_views_bp.route("/credit")
def ecommerce_credit():
    logger.debug("ecommerce_credit()")
    return render_template(
        "ecommerce/credit.html",
        templatename=get_app_vertical(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        user_info=get_userinfo(),
        _scheme="https")
