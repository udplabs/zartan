import logging
from flask import session
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY

from utils.rest import RestUtil


class Email:
    logger = logging.getLogger(__name__)

    @staticmethod
    def send_mail(subject, message, recipients):
        Email.logger.debug("send_mail()")
        logging.debug(recipients)
        url = "https://tjfvw6nb97.execute-api.us-east-2.amazonaws.com/prod/sendmail"
        headers = {
            "x-api-key": session[SESSION_INSTANCE_SETTINGS_KEY]["settings"]["sparkpost_api_key"],
            "Content-Type": "application/json"
        }
        body = {
            "to": recipients[0]['address'],
            "from": "udpsystem@udp.awsapps.com",
            "subject": subject,
            "text": message
        }
        return RestUtil.execute_post(url, body, headers=headers)
