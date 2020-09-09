import logging
from flask import session
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY

from utils.rest import RestUtil


class Email:
    logger = logging.getLogger(__name__)

    @staticmethod
    def send_mail(subject, message, recipients):
        Email.logger.debug("send_mail()")

        if len(session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["sparkpost_api_key"]) > 0:
            response = Email.send_mail_via_sparkpost(subject=subject, message=message, recipients=recipients)
        else:
            response = Email.send_mail_via_aws(subject=subject, message=message, recipients=recipients)

        Email.logger.debug(response)

    @staticmethod
    def send_mail_via_aws(subject, message, recipients):
        Email.logger.debug("send_mail_via_aws()")
        logging.debug(recipients)

        url = "https://tjfvw6nb97.execute-api.us-east-2.amazonaws.com/prod/sendmail"

        headers = {
            "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["aws_api_key"],
            "Content-Type": "application/json"
        }
        body = {
            "to": recipients[0]['address'],
            "from": "udpsystem@udp.awsapps.com",
            "subject": subject,
            "text": message
        }
        return RestUtil.execute_post(url, body, headers=headers)

    @staticmethod
    def send_mail_via_sparkpost(subject, message, recipients):
        Email.logger.debug("send_mail_via_sparkpost()")
        url = "https://api.sparkpost.com/api/v1/transmissions"

        headers = {
            "Authorization": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["sparkpost_api_key"],
            "Content-Type": "application/json"
        }
        body = {
            "options": {
                "sandbox": False
            },
            "content": {
                "from": "noreply@{domain}".format(domain=session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["sparkpost_from_domain"]),
                "subject": subject,
                "html": message
            },
            "recipients": recipients
        }
        return RestUtil.execute_post(url, body, headers=headers)
