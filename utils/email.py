import os
import base64
import json
import requests
from config import default_settings


from utils.rest import RestUtil

class Email:
    
    @staticmethod
    def send_mail(subject, message, recipients):
        print("send_mail()")
        url = "https://api.sparkpost.com/api/v1/transmissions"
        headers = {
            "Authorization": default_settings["SPARKPOST_API_KEY"],
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
        #return self.execute_post(url, body, headers=headers)