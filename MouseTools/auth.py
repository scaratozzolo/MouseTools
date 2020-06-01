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
        headers = {"authorization":"BEARER {}".format(access_token), "grant_type":"assertion", "assertion_type":"public", "client_id":"WDPRO-MOBILE.MDX.WDW.ANDROID-PROD"}
    else:
        headers = {"authorization":"BEARER {}".format(access_token)}

    return headers

def couchbaseHeaders():

    header = {"Authorization":"Basic RFBFQ1AtTU9CSUxFLldEVy5BTkRST0lELVBST0Q6RGhyeHMyZHVReGdiVjZ5Mg==","User-Agent":"CouchbaseLite/1.3 (1.4.1/8a21c5927a273a038fb3b66ec29c86425e871b11)","Content-Type":"application/json","Accept":"multipart/related"}
    return header
