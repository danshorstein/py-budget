import base64
from email.mime.text import MIMEText
from datetime import date
import os

import logbook
from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client import file, client, tools

gmail_log = logbook.Logger('gmail')

try:
    from services.secrets import login
except:
    from secrets import login

EMAIL = login['username']
SCOPES = 'https://www.googleapis.com/auth/gmail.compose'

def send_email(msg):
    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("services/credentials.json", SCOPES)
        creds = tools.run_flow(flow, store)
    service = build("gmail", "v1", http=creds.authorize(Http()))

    body = create_message(
        sender=EMAIL,
        to=EMAIL,
        subject=f"Budget Update {date.today()}",
        message=msg,
    )

    draft = service.users().messages().send(userId="me", body=body).execute()

    log_msg = f'Sent email {draft} to {EMAIL} dated {date.today()}'
    gmail_log.info(log_msg)
    print(log_msg)


def create_message(sender, to, subject, message):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message, "html")
    message["to"] = to
    # message["from"] = sender
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


if __name__ == "__main__":
    # msg = "<h1>HI!!!!!</h1></br><ul><li>hello</li><li>testing!!!!!</li></ul>"
    msg = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">

  <title></title>

  <style type="text/css">
  </style>    
</head>
<body style="margin:0; padding:0; background-color:#F2F2F2;">
  <center>
    <table width="100%" border="0" cellpadding="0" cellspacing="0" bgcolor="#F2F2F2">
        <tr>
            <td align="center" valign="top">
                testing!
                
            </td>
        </tr>
    </table>
  </center>
</body>
</html>'''
    
    send_email(msg)
