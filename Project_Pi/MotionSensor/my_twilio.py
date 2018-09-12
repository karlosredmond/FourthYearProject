#    Copyright 2018 Karl Redmond
#    Filename: my_twilio.py
#    Author:   Karl Redmond
#    Date:     18/04/2018
#    Brief:    Twilio credentials used for sending SMS messages

from twilio.rest import Client

account_sid = "AC0192978da4c454938b9f0cd97a0a675a"
auth_token = "cae865e31a8bbba6769bb725da7a0f10"
# Live Credentials account_sid = "ACc5f0347054e7b0d8ce2af0cf198b5a38"
# Live Credentials auth_token = "d06e040847125ab35fff6cd205292825"
client = Client(account_sid, auth_token)