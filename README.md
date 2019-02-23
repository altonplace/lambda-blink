# Lambda-Blink

Basic Interface for toggling armed status for Blink Cameras.  Includes integration with Slack to communicate the status.

### Blink variables
To get your region and network, run this command substituting your username and password.  
```
curl -H "Host: prod.immedia-semi.com" -H "Content-Type: application/json" --data-binary '{ "password" : "your blink password", "client_specifier" : "iPhone 9.2 | 2.2 | 222", "email" : "your blink login/email" }' --compressed https://rest.prod.immedia-semi.com/login
```

### Slack variables

Follow this guide to get a url:
https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack

### CloudFormation
Update the template.yaml.sample with the proper environment variables and rename to ```template.yaml```.

Deploy to your AWS account.  Easiest way is to use the Pycharm AWSToolkit plugin.

