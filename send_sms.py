import os
from twilio.rest import Client


account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
my_num = os.environment['TWILIO_NUMBER']
client = Client(account_sid, auth_token)

def send_reminder_text(to, msg):
    message = client.messages \
    .create(
         body=msg,
         from_=my_num,
         to=to
     )

    print(message.sid)
    print(message.status)