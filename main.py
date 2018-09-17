import requests
import os
import json

# Set Envionmental Variables
auth_token = os.environ['auth_token']
region = os.environ['region']
network = os.environ['network']
discord_url = os.environ['discord_url']


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


class Blink(object):
    def __init__(self):
        self.auth_token = auth_token
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
