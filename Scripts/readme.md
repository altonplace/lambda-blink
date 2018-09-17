##CURL Requests for reference:

From:  https://github.com/MattTW/BlinkMonitorProtocol

###Get Token:
curl -H "Host: prod.immedia-semi.com" -H "Content-Type: application/json" 
--data-binary '{ "password" : "your blink password", "client_specifier" : "iPhone 9.2 | 2.2 | 222", "email" : "your blink login/email" }' --compressed https://rest.prod.immedia-semi.com/login

###Get Network:

curl -H "Host: prod.immedia-semi.com" -H "TOKEN_AUTH: authtoken from login" --compressed https://rest.prod.immedia-semi.com/networks

###Sync Status:
curl -H "Host: prod.immedia-semi.com" -H "TOKEN_AUTH: authtoken from login" --compressed https://rest.prod.immedia-semi.com/network/*network_id_from_networks_call*/syncmodules

###Arm System:
curl -H "Host: prod.immedia-semi.com" -H "TOKEN_AUTH: authtoken from login" --data-binary --compressed https://rest.prod.immedia-semi.com/network/*network_id_from_networks_call*/arm

###Disarm System:
curl -H "Host: prod.immedia-semi.com" -H "TOKEN_AUTH: authtoken from login" --data-binary --compressed https://rest.prod.immedia-semi.com/network/*network_id_from_networks_call*/disarm



