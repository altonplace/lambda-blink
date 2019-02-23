import requests
import os
import json
import re

# Get/Set Environmental Variables
region = os.environ['BlinkRegion']
network = os.environ['BlinkNetwork']
user = os.environ['BlinkUser']
passw = os.environ['BlinkPass']
slack_url = os.environ['SlackUrl']


def send_message_slack(url, message):
    payload = {"text": message}

    data = json.dumps(payload)
    headers = {'Content-Type': 'application/json'}

    r = requests.post(url, data=data, headers=headers)

    if r.status_code != 200:
        print('post failed with error', r.status_code, 'because', r.reason)
    else:
        print('post success')
    return r


class Blink(object):
    def __init__(self):
        self.auth_token = 'unset token'
        self.get_token()
        self.region = region
        self.network = network

    def get_token(self):

        url = 'https://rest.prod.immedia-semi.com/login'
        headers = {'Host': "prod.immedia-semi.com",
                   'Content-Type': 'application/json'}

        data = json.dumps({"email": user,
                           "password": passw,
                           "client_specifier": "iPhone 9.2 | 2.2 | 222"
                           })

        r = requests.post(url, headers=headers, data=data)

        self.auth_token = re.search(r'{\"authtoken\":\"(.*?)\"', r.text).group(1)

    def get_status(self):

        url = 'https://rest.{}.immedia-semi.com/network/{}/syncmodules'.format(self.region, self.network)
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
                message = 'House is unarmed'

            url = 'https://rest.{}.immedia-semi.com/network/{}/{}'.format(self.region, self.network, state)

            r = requests.post(url, headers={'TOKEN_AUTH': self.auth_token})

            send_message_slack(slack_url, message)

            return r.text


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
