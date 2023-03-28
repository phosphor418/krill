from __future__ import print_function

import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']
BLACKLIST_NAMES = open("blacklist_names.txt")
BLACKLIST_NAMES = BLACKLIST_NAMES.read().splitlines()
BLACKLIST_EMAILS = open("blacklist_emails.txt")
BLACKLIST_EMAILS = BLACKLIST_EMAILS.read().splitlines()

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        while True:
            service = build('gmail', 'v1', credentials=creds)

            messages = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
            list_messages = messages.get('messages', [])

            for message in list_messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                id = message['id']
                headers = msg['payload']['headers']

                for data in headers:
                    name = data['name']
                    if name == 'From':
                        sender = data['value']
                        if "<" in sender:
                            splitted_name = sender.split('<')[0].rstrip()
                            splitted_name.replace('"', '')
                            splitted_email = sender.split('<')[1].replace('>', '')
                        else:
                            splitted_name = sender
                            splitted_email = sender
                        if splitted_name in BLACKLIST_NAMES or splitted_email in BLACKLIST_EMAILS:
                            service.users().messages().delete(userId='me', id=id).execute()
            time.sleep(900)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()