import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

udp_config = {
    "issuer": os.getenv("UDP_ISSUER", "https://udp.okta.com/oauth2/default"),
    "client_id": os.getenv("UDP_CLIENT_ID", ""),
    "client_secret": os.getenv("UDP_CLIENT_SECRET", "")
}
