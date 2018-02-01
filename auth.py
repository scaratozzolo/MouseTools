import requests
import json



#Gets an authentication(access) token from Disney
def Authenticaton():
    r = requests.get("https://disneyworld.disney.go.com/authentication/get-client-token")
    auth = json.loads(r.text)
    return auth['access_token']
