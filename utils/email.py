import os
from flask import session
from utils.udp import SESSION_INSTANCE_SETTINGS_KEY

from utils.rest import RestUtil


class Email:

    @staticmethod
    def send_mail(subject, message, recipients):
        print("send_mail()")
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
                "from": "noreply@recintodev.com",
                "subject": subject,
                "html": message
            },
            "recipients": recipients
        }
        return RestUtil.execute_post(url, body, headers=headers)
