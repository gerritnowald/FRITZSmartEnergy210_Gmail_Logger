"""downloads email attachments from Gmail messages with a specific label, optionally moves messages to trash"""

from googleapiclient.discovery import build

import base64
import argparse
import os

from authentication.auth import authenticate

# -------------------------------------------------------------
# user input

argparser = argparse.ArgumentParser(description="Download attachments from Gmail messages with a specific label.")
argparser.add_argument('labelID', type=str, help="Use 'get_label_ids.py' to find the label ID.")
argparser.add_argument("-d", "--data_dir", type=str, default="./attachments",
                       help="Directory downloaded attachments are saved to (default: ./attachments).")
argparser.add_argument("-t", "--trash", action='store_true',
                       help="Move messages to trash after downloading.")

labelId  = argparser.parse_args().labelID
data_dir = argparser.parse_args().data_dir
trash    = argparser.parse_args().trash

# -------------------------------------------------------------
# authenticate

creds   = authenticate()
service = build("gmail", "v1", credentials=creds)

# -------------------------------------------------------------
# get message ids with specific label

msgIds = ( service.users().messages()
    .list(userId="me", labelIds=[labelId]).execute() )

try:
    msgIds = [msg['id'] for msg in msgIds['messages']]
    print(f"{len(msgIds)} messages found")
except KeyError:
    msgIds = []
    print("No messages found")

# -------------------------------------------------------------
# create data directory if it doesn't exist

if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Created directory {data_dir}")

# -------------------------------------------------------------
# function to get filenames and attachment IDs

def get_attachments(parts, attIds, filenames):
    for part in parts:
        if 'filename' in part and 'attachmentId' in part.get('body', {}):
            filenames.append(part['filename'])
            attIds.append(part['body']['attachmentId'])
        if 'parts' in part:
            get_attachments(part['parts'], attIds, filenames)

# -------------------------------------------------------------
# get messages

for msgId in msgIds:
    print(' ')
    message = service.users().messages().get(userId="me", id=msgId).execute()

# -------------------------------------------------------------
# get attachments ids

    attIds    = []
    filenames = []
    get_attachments(message['payload'].get('parts', []), attIds, filenames)

# -------------------------------------------------------------
# download attachments
# https://stackoverflow.com/questions/25832631/download-attachments-from-gmail-using-gmail-api

    for attId, filename in zip(attIds, filenames):
        att = (service.users().messages().
            attachments().get(userId="me", messageId=msgId, id=attId).execute() )
        
        file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))

        path = os.path.join(data_dir, filename)
        with open(path, 'wb') as f:
            f.write(file_data)
            print(f"Downloaded {filename} to {data_dir}")

# -------------------------------------------------------------
# move messages to trash

    if trash:    
        for header in message['payload']['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
                break

        service.users().messages().trash(userId="me", id=msgId).execute()
        print(f"Message '{subject}' moved to trash")