import requests
import json
from datetime import datetime, timedelta


def Authentication():
    """Gets an authentication(access) token from Disney and returns it"""

    r = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token")
    auth = json.loads(r.content)
    return auth['access_token'], auth['expires_in']


time_of_expire = None
access_token = None

def getHeaders():
    """Creates the headers to send during the request and returns it"""

    global time_of_expire
    global access_token

    if time_of_expire == None or (datetime.now() > time_of_expire):
        access_token, expires_in = Authentication()
        time_of_expire = datetime.now() + timedelta(seconds=(expires_in-10))
        headers = {"Authorization":"BEARER {}".format(access_token)}
    else:
        headers = {"Authorization":"BEARER {}".format(access_token)}

    return headers
