#    Copyright 2018 Karl Redmond
#    Filename: my_twilio.py
#    Author:   Karl Redmond
#    Date:     18/04/2018
#    Brief:    Twilio credentials used for sending SMS messages

from twilio.rest import Client

account_sid = ""
auth_token = ""
# Live Credentials account_sid = ""
# Live Credentials auth_token = ""
client = Client(account_sid, auth_token)
