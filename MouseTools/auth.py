import requests
import json
from datetime import datetime, timedelta


def Authentication():
    """Gets an authentication (access) token from Disney and returns it"""

    headers = {"User-Agent":"CouchbaseLite/1.3 (1.4.1/8a21c5927a273a038fb3b66ec29c86425e871b11)","Content-Type":"application/json","Accept":"multipart/related"}
    auth = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token", headers=headers).json()
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
        headers = {"Authorization":"BEARER {}".format(access_token), "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", "Content-Type":"application/json;charset=UTF-8","Accept":"*/*"}
    else:
        headers = {"Authorization":"BEARER {}".format(access_token), "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", "Content-Type":"application/json;charset=UTF-8","Accept":"*/*"}

    return headers

def couchbaseHeaders():

    header = {"Authorization":"Basic RFBFQ1AtTU9CSUxFLldEVy5BTkRST0lELVBST0Q6RGhyeHMyZHVReGdiVjZ5Mg==","User-Agent":"CouchbaseLite/1.3 (1.4.1/8a21c5927a273a038fb3b66ec29c86425e871b11)","Content-Type":"application/json","Accept":"multipart/related"}
    return header
