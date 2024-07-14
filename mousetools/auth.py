import requests
import json
from datetime import datetime, timedelta


def disney_authentication():
    """Gets an authentication (access) token from Disney and returns it"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept-Language' : 'en_US',
        'Cache-Control' : '0',
        'Accept' : 'application/json',
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Connection' : 'keep-alive',
        'Proxy-Connection' : 'keep-alive',
        'Accept-Encoding' : 'gzip, deflate'
    }
    auth = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token", headers=headers, timeout=10).json()
    return auth['access_token'], auth['expires_in']


time_of_expire = None
access_token = None

def get_headers():
    """Creates the headers to send during the request and returns it"""

    global time_of_expire
    global access_token

    if time_of_expire == None or (datetime.now() > time_of_expire):
        access_token, expires_in = disney_authentication()
        time_of_expire = datetime.now() + timedelta(seconds=(expires_in-10))

    headers = {"Authorization":"BEARER {}".format(access_token), "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', "Content-Type":"application/json;charset=UTF-8","Accept":"*/*"}

    return headers

if __name__ == '__main__':

    print(get_headers())
