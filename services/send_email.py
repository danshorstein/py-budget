import base64
from email.mime.text import MIMEText
from datetime import date
import os

import logbook
from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client import file, client, tools

gmail_log = logbook.Logger('gmail')

base_path = os.path.dirname(__file__)

try:
    from services.secrets import login, recipients
except:
    from secrets import login, recipients

EMAIL = login['username']
RECIPIENTS = recipients
SCOPES = 'https://www.googleapis.com/auth/gmail.compose'

def send_email(msg):
    store = file.Storage(os.path.join(base_path, "token.json"))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(
            os.path.join(base_path, "credentials.json"), SCOPES)
        creds = tools.run_flow(flow, store)
    service = build("gmail", "v1", http=creds.authorize(Http()))

    body = create_message(
        sender=EMAIL,
        to=', '.join(RECIPIENTS),
        subject=f"Budget Update {date.today()}",
        message=msg,
    )

    draft = service.users().messages().send(userId="me", body=body).execute()

    log_msg = f'Sent email {draft} to {", ".join(RECIPIENTS)} dated {date.today()}'
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
