import requests
import os
import json
import re

# Set Envionmental Variables
region = os.environ['region']
network = os.environ['network']
discord_url = os.environ['discord_url']
user = os.environ['user']
passw = os.environ['passw']


def send_message_discord(url, message):
    payload = {'username': 'Blink',
               'content': message
               }
    data = json.dumps(payload)
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=data, headers=headers)
    if r.status_code != 204:
        print('post failed with error', r.status_code, 'because', r.reason)
    else:
        print('post success')
    return r


def get_token():

    url = 'https://rest.prod.immedia-semi.com/login'
    headers = {'Host': "prod.immedia-semi.com",
               'Content-Type': 'application/json'}

    data = json.dumps({"email": user,
                       "password": passw,
                       "client_specifier": "iPhone 9.2 | 2.2 | 222"
                       })

    r = requests.post(url, headers=headers, data=data)

    auth_token = re.search(r'{\"authtoken\":\"(.*?)\"', r.text).group(1)

    return auth_token


class Blink(object):
    def __init__(self):
        self.auth_token = get_token()
        self.region = region
        self.network = network

    def get_status(self):
        # Build URL
        url = 'https://rest.{}.immedia-semi.com/network/{}/syncmodules'.format(self.region, self.network)
        print(url)
        r = requests.get(url, headers={'TOKEN_AUTH': self.auth_token})
        return r.text

    def alarm_set(self, state='arm'):
        state = state
        if state.upper() not in ('ARM', 'DISARM'):
            print("Invalid Input: alarm_set must be in either arm or disarm")
        else:
            if state.upper() == 'ARM':
                message = 'House is armed'
            if state.upper() == 'DISARM':
                message = 'House is disarmed'
            # Build URL
            url = 'https://rest.{}.immedia-semi.com/network/{}/{}'.format(self.region, self.network, state)
            print(url)
            r = requests.post(url, headers={'TOKEN_AUTH': self.auth_token})
            send_message_discord(discord_url, message)

            return r.text


# Main

Blink = Blink()


def lambda_handler(event, context):
    clickType = event['clickType']

    if clickType == 'SINGLE':
        r = Blink.alarm_set('arm')
    elif clickType == 'DOUBLE':
        r = Blink.alarm_set('disarm')
    else:
        r = 'No Action'
    return r
