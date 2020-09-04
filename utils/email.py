import logging
from flask import session
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY

from utils.rest import RestUtil


class Email:
    logger = logging.getLogger(__name__)

    @staticmethod
    def send_mail(subject, message, recipients):
        Email.logger.debug("send_mail()")
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
