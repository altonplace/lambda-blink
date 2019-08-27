import requests
import os
import json
import boto3
from botocore.exceptions import ClientError

# Get/Set Environmental Variables
ssm_secret_name = os.environ['SSMSecretName'] if 'SSMSecretName' in os.environ else 'prod/blink/login'
ssm_region = os.environ['SSMRegion'] if 'SSMRegion' in os.environ else 'us-east-1'
slack_url = os.environ['SlackUrl'] if 'SlackUrl' in os.environ else None


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
        self.session = boto3.session.Session()
        self.ssm_secret_name = ssm_secret_name
        self.ssm_region = ssm_region
        self.ssm = self.session.client(service_name='secretsmanager', region_name=self.ssm_region)
        self.email = None
        self.password = None
        self.auth_token = None
        self.region = None
        self.network = None
        self.get_secrets()
        self.get_token()


    def get_secrets(self):
        try:
            ssm_secret = self.ssm.get_secret_value(SecretId=self.ssm_secret_name)
            if 'SecretString' in ssm_secret:
                self.email = json.loads(ssm_secret['SecretString'])['blinkUser']
                self.password = json.loads(ssm_secret['SecretString'])['blinkPassword']
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise e
            else:
                raise e


    def update_secrets(self, email, password):
        secret = {
            'blinkUser' : email,
            'blinkPassword' : password}
        try:
            ssm_update_secret = self.ssm.update_secret(SecretId=self.ssm_secret_name, SecretString=json.dumps(secret))
        except ClientError as e:
            raise e
        
        self.email = email
        self.password = password
        return ssm_update_secret


    def get_token(self):
        
        url = 'https://rest.prod.immedia-semi.com/login'
        headers = {'Host': "prod.immedia-semi.com",
                   'Content-Type': 'application/json'}

        data = json.dumps({"email": self.email,
                           "password": self.password,
                           "client_specifier": "iPhone 9.2 | 2.2 | 222"
                           })

        r = requests.post(url, headers=headers, data=data)
        
        if 'authtoken' in json.loads(r.text):
            self.auth_token = json.loads(r.text)['authtoken']['authtoken']
            self.region = [rgn for rgn in json.loads(r.text)['region'].keys() if 'region' in json.loads(r.text)]
            self.network = [nwk for nwk in json.loads(r.text)['networks'].keys() if 'networks' in json.loads(r.text)]
        else:
            return r.text


    def get_status(self):
        url = 'https://rest.{}.immedia-semi.com/network/{}/syncmodules'.format(self.region[0], self.network[0])
        r = requests.get(url, headers={'TOKEN_AUTH': self.auth_token})
        return r.text


    def alarm_set(self, state='arm'):
        if state.upper() not in ('ARM', 'DISARM'):
            print("Invalid Input: alarm_set must be in either arm or disarm")
        else:
            if state.upper() == 'ARM':
                message = 'House is armed'

            if state.upper() == 'DISARM':
                message = 'House is unarmed'

            url = 'https://rest.{}.immedia-semi.com/network/{}/{}'.format(self.region[0], self.network[0], state.lower())
            r = requests.post(url, headers={'TOKEN_AUTH': self.auth_token})

            if slack_url:
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
