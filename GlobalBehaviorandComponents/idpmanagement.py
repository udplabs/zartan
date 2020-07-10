import logging
import xml.etree.ElementTree as ET

# import functions
from flask import render_template, session, request, redirect, url_for
from flask import Blueprint
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_app_vertical
from utils.okta import TokenUtil, OktaAdmin, IDPUtil

from GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo

logger = logging.getLogger(__name__)

# set blueprint
gbac_manageidps_bp = Blueprint(
    'gbac_manageidps_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='static')

@gbac_manageidps_bp.route("/managesamlidps")
@is_authenticated
def gbac_saml_idps():
    logger.debug("gbac_saml_idps()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    idp_list = okta_admin.get_idps()

    for idp in idp_list:
        if idp['type'] != 'SAML2':
            idp_list.remove(idp)

    logger.debug(idp_list)
    return render_template(
        "/managesamlidps.html",
        templatename=get_app_vertical(),
        user_info=get_userinfo(),
        idplist=idp_list,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])

@gbac_manageidps_bp.route("/managesamlidp")
@is_authenticated
def gbac_create_update_saml_idp_page():
    logger.debug("gbac_create_update_saml_idp_page()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    idp_id = request.args.get('idpId')
    idp_info = okta_admin.get_idp(idp_id)

    if 'id' in idp_info:
        cert_info = okta_admin.get_idp_certificate(idp_info['protocol']['credentials']['trust']['kid'])
        cert_display_data = IDPUtil.getCertificateDisplayValues(cert_info['x5c'][0])
        idp_info['cert_expiry'] = cert_display_data.not_valid_after
        idp_info['cert_issuer'] = cert_display_data.issuer.rfc4514_string()

    logger.debug("Retrieved IDP: {0}".format(idp_info))
    return render_template(
        "/managesamlidp.html",
        templatename=get_app_vertical(),
        id_token=TokenUtil.get_id_token(request.cookies),
        access_token=TokenUtil.get_access_token(request.cookies),
        idp_info=idp_info,
        config=session[SESSION_INSTANCE_SETTINGS_KEY])

@gbac_manageidps_bp.route("/updatesamlidp", methods=["POST"])
@is_authenticated
def gbac_update_saml_idp():
    logger.debug("gbac_update_saml_idp()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])
    idpMetadataFile = request.files.get('idpMetadata')

    #If we're updating, we need to pull current data.
    if request.form.get('idpId'):
        idpAPIData = okta_admin.get_idp(request.form.get('idpId'))
    else:
        idpAPIData = IDPUtil.getIDPModel()

    idpAPIData['name'] = request.form.get('idpName')

    if idpMetadataFile:
        #Use metadata here.
        logger.info("Metadata uploaded. Parsing...")
        data = IDPUtil.parseIDPMetadata(idpMetadataFile.read())
        idpAPIData['protocol']['endpoints']['sso']['url'] = data['ssoUrl']
        idpAPIData['protocol']['endpoints']['sso']['binding'] = data['bindingType']
        idpAPIData['protocol']['endpoints']['sso']['destination'] = data['ssoUrl']
        idpAPIData['protocol']['credentials']['trust']['issuer'] = data['entityID']
        certData = data['signingCert']
    else:
        logger.info("Using manual entry.")
        idpCertificateFile = request.files.get('idpCertificate')
        idpAPIData['protocol']['credentials']['trust']['issuer'] = request.form.get('idpIssuer')
        idpAPIData['protocol']['endpoints']['sso']['url'] = request.form.get('ssoUrl')
        idpAPIData['protocol']['endpoints']['sso']['destination'] = request.form.get('ssoUrl')
        certData = IDPUtil.parseX509File(idpCertificateFile)

    if certData:
        kid = IDPUtil.getCertificateKid(certData, okta_admin)
    else:
        #Unlike other form inputs, if we're not changing the cert in update mode, the cert file upload will be null instead of filled out.
        #so rather than loading from formdata like normal, we have to load from the fetched Okta data.
        kid = idpAPIData['protocol']['credentials']['trust']['kid']

    if not kid:
        logger.info("Certificate not in store yet- uploading.")
        idp_cert_data = {"x5c": [certData]}
        resp = okta_admin.upload_idp_certificate(idp_cert_data)
        logger.info(resp)

        if "kid" in resp:
            kid = resp["kid"]
        elif "errorCode" in resp:
            logger.error(resp)
            #How do i handle the error properly here?
        else:
            logger.error("An exception was thrown.")
    else:
        logger.info("Certificate already in store- using kid: {0}".format(kid))

    idpAPIData['protocol']['credentials']['trust']['kid'] = kid

    logger.info("About to upload! {0}".format(idpAPIData))

    if request.form.get('idpId'):
        resp = okta_admin.update_idp(request.form.get('idpId'), idpAPIData)
    else: #Create.
        resp = okta_admin.create_idp(idpAPIData)

    logger.info(resp)
    return redirect(url_for("gbac_manageidps_bp.gbac_saml_idps", _external="True", _scheme="http", message="Success!"))

@gbac_manageidps_bp.route("/activatesamlidp")
@is_authenticated
def gbac_activatesamlidp():
    logger.debug("activatesamlidp()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    if request.args.get('idpId'):
        resp = okta_admin.activate_idp(request.args.get('idpId'))

    logger.info(resp)
    return redirect(url_for("gbac_manageidps_bp.gbac_saml_idps", _external="True", _scheme="http", message="Success!"))

@gbac_manageidps_bp.route("/deactivatesamlidp")
@is_authenticated
def gbac_deactivatesamlidp():
    logger.debug("deactivatesamlidp()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    if request.args.get('idpId'):
        resp = okta_admin.deactivate_idp(request.args.get('idpId'))

    logger.info(resp)
    return redirect(url_for("gbac_manageidps_bp.gbac_saml_idps", _external="True", _scheme="http", message="Success!"))

@gbac_manageidps_bp.route("/deletesamlidp")
@is_authenticated
def gbac_deletesamlidp():
    logger.debug("deletesamlidp()")
    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])

    if request.args.get('idpId'):
        resp = okta_admin.delete_idp(request.args.get('idpId'))

    logger.info(resp)
    return redirect(url_for("gbac_manageidps_bp.gbac_saml_idps", _external="True", _scheme="http", message="Success!"))
