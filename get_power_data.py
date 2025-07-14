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

label_id = argparser.parse_args().labelID
data_dir = argparser.parse_args().data_dir
trash    = argparser.parse_args().trash

# -------------------------------------------------------------
# functions to download attachments from Gmail messages
# https://stackoverflow.com/questions/25832631/download-attachments-from-gmail-using-gmail-api

def DownloadAttachments(service, msg_id, att_id, filename):
    att = service.users().messages().attachments().get(userId="me", messageId=msg_id,id=att_id).execute()
    file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))

    path = os.path.join(data_dir, filename)
    with open(path, 'wb') as f:
        f.write(file_data)
        print(f"Downloaded {filename} to {data_dir}")


def get_attachment_ID(service, msg_id, message):
    for part in message['payload']['parts']:
        if not part['filename']:
            continue

        att_id = part['body']['attachmentId']
        filename = part['filename']
        
        DownloadAttachments(service, msg_id, att_id, filename)


def get_inline_ID(service, msg_id, message):
    att_id   = message['payload']['parts'][0]['parts'][2]['body']['attachmentId']
    filename = message['payload']['parts'][1]['filename'][:-4] + "_temperature.png"

    DownloadAttachments(service, msg_id, att_id, filename)

# -------------------------------------------------------------
# authenticate

creds = authenticate()
service = build("gmail", "v1", credentials=creds)

# -------------------------------------------------------------
# get message ids with specific label

msg_ids = ( service.users().messages()
    .list(userId="me", labelIds=[label_id]).execute() )

try:
    msg_ids = [msg['id'] for msg in msg_ids['messages']]
    print(f"{len(msg_ids)} messages found")
except KeyError:
    msg_ids = []
    print("No messages found")

# -------------------------------------------------------------
# download attachments and move messages to trash

if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory {data_dir}")


for id in msg_ids:
    print(' ')

    message = service.users().messages().get(userId="me", id=id).execute()


    get_attachment_ID(service, id, message)

    get_inline_ID(service, id, message)


    if not trash:
        continue
    
    for header in message['payload']['headers']:
        if header['name'] == 'Subject':
            subject = header['value']
            break

    service.users().messages().trash(userId="me", id=id).execute()
    print(f"Message '{subject}' moved to trash")