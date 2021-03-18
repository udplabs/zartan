import logging

from random import randint
from flask import render_template, session, redirect, url_for, request
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from utils.okta import TokenUtil, OktaAdmin


from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
developer_views_bp = Blueprint('developer_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@developer_views_bp.route("/developerhome")
@is_authenticated
def developer_home():
    logger.debug("developer_home()")
    return render_template("developer/developerhome.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY])


@developer_views_bp.route("/profile")
@is_authenticated
def developer_profile():
    logger.debug("developer_profile()")

    return render_template(
        "developer/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@developer_views_bp.route("/users_advanced")
@is_authenticated
def developer_usersadvanced():
    logger.debug("developer_usersadvanced()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_groups = okta_admin.get_groups_by_name("everyone")
    if len(user_groups) > 0:
        # just grab the first one... there should only be one match for now
        logger.debug(user_groups)
        user_group = user_groups[0]

    group_id = user_group["id"]
    group_user_list = okta_admin.get_user_list_by_group_id(group_id)

    return render_template(
        "/developer/users_advanced.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        userlist=group_user_list,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        user_group=user_group)


@developer_views_bp.route("/temporarypasscode")
@is_authenticated
def developer_temporarypasscode():
    logger.debug("developer_temporarypasscode()")
    user_id = request.args.get('user_id')

    randcode = random_with_N_digits(6)

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    listfactors = okta_admin.list_enrolled_factors(user_id)
    for factor_info in listfactors:
        if "question" in factor_info['factorType']:
            factor_id = factor_info['id']
            okta_admin.delete_factor(user_id=user_id, factor_id=factor_id)
            okta_admin.enroll_securityquestion(user_id, "favorite_security_question", str(randcode))
        else:
            okta_admin.enroll_securityquestion(user_id, "favorite_security_question", str(randcode))

    message = "Your Temporary Code is: {0}".format(str(randcode))

    return redirect(
        url_for(
            "developer_views_bp.developer_usersadvanced",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            message=message))


def random_with_N_digits(n):
    range_start = 10**(n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


@developer_views_bp.route("/users_keysetup")
@is_authenticated
def developer_userskeysetup():
    logger.debug("users_keysetup()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_groups = okta_admin.get_groups_by_name("everyone")
    if len(user_groups) > 0:
        # just grab the first one... there should only be one match for now
        logger.debug(user_groups)
        user_group = user_groups[0]

    group_id = user_group["id"]
    group_user_list = okta_admin.get_user_list_by_group_id(group_id)

    return render_template(
        "/developer/users_keysetup.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        userlist=group_user_list,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        user_group=user_group)


@developer_views_bp.route("/addkey")
@is_authenticated
def developer_addkeytouser():
    logger.debug("developer_addkeytouser()")
    user_id = request.args.get('userId')
    factor_profile_id = request.args.get('factorProfileId')
    shared_secret = request.args.get('sharedSecret')

    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    listfactors = okta_admin.list_enrolled_factors(user_id)
    logger.debug(listfactors)
    for factor_info in listfactors:
        if "token:hotp" in factor_info['factorType']:
            factor_id = factor_info['id']
            okta_admin.delete_factor(user_id=user_id, factor_id=factor_id)
            response = okta_admin.enroll_hardtoken(user_id, factor_profile_id, shared_secret)
            logger.debug(response)
            break
        else:
            response = okta_admin.enroll_hardtoken(user_id, factor_profile_id, shared_secret)
            logger.debug(response)
            break

    message = "Your Key is Setup"

    return message
