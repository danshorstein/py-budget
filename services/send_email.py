import base64
from email.mime.text import MIMEText
from datetime import date

from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client import file, client, tools

from services.secrets import login

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
        EMAIL,
        EMAIL,
        f"Budget Update {date.today()}",
        msg,
    )

    draft = service.users().messages().send(userId="me", body=body).execute()

    print(draft)


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
    msg = "<h1>HI!!!!!</h1></br><ul><li>hello</li><li>testing!!!!!</li></ul>"
    send_email(msg)
