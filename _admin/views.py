import logging
import json

# import functions
from random import randint
from flask import render_template, session, redirect, url_for, request
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical, apply_remote_config
from utils.okta import TokenUtil, OktaAdmin


from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
admin_views_bp = Blueprint('admin_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')


# Required for Login Landing Page
@admin_views_bp.route("/adminhome")
@apply_remote_config
@is_authenticated
def admin_home():
    logger.debug("admin_home()")
    return render_template("admin/adminhome.html", user_info=get_userinfo(), config=session[SESSION_INSTANCE_SETTINGS_KEY])


@admin_views_bp.route("/profile")
@apply_remote_config
@is_authenticated
def admin_profile():
    logger.debug("admin_profile()")

    return render_template(
        "admin/profile.html",
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"])


@admin_views_bp.route("/users_advanced")
@apply_remote_config
@is_authenticated
def admin_usersadvanced():
    logger.debug("admin_usersadvanced()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    user_groups = okta_admin.get_groups_by_name("everyone")
    if len(user_groups) > 0:
        # just grab the first one... there should only be one match for now
        logger.debug(user_groups)
        user_group = user_groups[0]

    group_id = user_group["id"]
    group_user_list = okta_admin.get_user_list_by_group_id(group_id)

    return render_template(
        "/admin/users_advanced.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        userlist=group_user_list,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        user_group=user_group)


@admin_views_bp.route("/temporarypasscode")
@apply_remote_config
@is_authenticated
def admin_temporarypasscode():
    logger.debug("admin_temporarypasscode()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    user_id = request.args.get('user_id')
    user = okta_admin.get_user(user_id)
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

    usersname = user["profile"]["firstName"] + " " + user["profile"]["lastName"]

    message = "{0} - MFA Security Question Set to 'Favorite Security Question'. Users new code is: {1}".format(usersname, str(randcode))

    return redirect(
        url_for(
            "admin_views_bp.admin_usersadvanced",
            _external="True",
            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],
            message=message))


def random_with_N_digits(n):
    range_start = 10**(n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


@admin_views_bp.route("/users_keysetup")
@apply_remote_config
@is_authenticated
def admin_userskeysetup():
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
        "/admin/users_keysetup.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        userlist=group_user_list,
        config=session[SESSION_INSTANCE_SETTINGS_KEY],
        user_group=user_group)


@admin_views_bp.route("/addkey")
@apply_remote_config
@is_authenticated
def admin_addkeytouser():
    logger.debug("admin_addkeytouser()")
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


@admin_views_bp.route("/getfactors")
@apply_remote_config
def admin_getfactors():
    logger.debug("admin_userverification()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    user_id = request.args.get('user_id')
    listfactors = okta_admin.list_enrolled_factors(user_id)

    return json.dumps(listfactors)


@admin_views_bp.route("/sendfactor")
@apply_remote_config
def admin_sendfactor():
    logger.debug("admin_sendfactor()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    user_id = request.args.get('user_id')
    factor_id = request.args.get('factor_id')

    response = okta_admin.send_push(user_id, factor_id)
    return json.dumps(response)


@admin_views_bp.route("/verifyfactor")
@apply_remote_config
def admin_verifyfactor():
    logger.debug("admin_verifyfactor()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    user_id = request.args.get('user_id')
    factor_id = request.args.get('factor_id')
    code = request.args.get('code')

    response = okta_admin.verify_push(user_id, factor_id, code)
    return json.dumps(response)
