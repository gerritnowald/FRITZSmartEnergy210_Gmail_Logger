from googleapiclient.discovery import build

import base64
import argparse
import os

from authentication.auth import authenticate

# -------------------------------------------------------------
# user input

argparser = argparse.ArgumentParser(description="Download attachments from Gmail messages with a specific label.")
argparser.add_argument('labelID', type=str, help="Use get_label_ids.py to find the label ID.")
argparser.add_argument("-d", "--data_dir", type=str, default="./data",
                       help="Directory downloaded attachments are saved to (default: ./data).")

label_id = argparser.parse_args().labelID
data_dir = argparser.parse_args().data_dir

# -------------------------------------------------------------
# function to download attachments from Gmail messages

# https://stackoverflow.com/questions/25832631/download-attachments-from-gmail-using-gmail-api
def DownloadAttachments(service, msg_id):
    """Get and store attachment from Message with given id. """
    message = service.users().messages().get(userId="me", id=msg_id).execute()

    for part in message['payload']['parts']:
        if part['filename']:
            if 'data' in part['body']:
                data = part['body']['data']
            else:
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(userId="me", messageId=msg_id,id=att_id).execute()
                data = att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

            path = os.path.join(data_dir, part['filename'])
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created directory {data_dir}")

            with open(path, 'wb') as f:
                f.write(file_data)
                print(f"Downloaded {part['filename']} to {data_dir}")

# -------------------------------------------------------------
# function to download inline images from Gmail messages

def DownloadInlineImages(service, msg_id):
    message = service.users().messages().get(userId="me", id=msg_id).execute()

    att_id = message['payload']['parts'][0]['parts'][2]['body']['attachmentId']
    att = service.users().messages().attachments().get(userId="me", messageId=msg_id,id=att_id).execute()
    file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))

    filename = message['payload']['parts'][1]['filename'][:-4] + "_temperature.png"
    path = os.path.join(data_dir, filename)

    with open(path, 'wb') as f:
        f.write(file_data)
        print(f"Downloaded {filename} to {data_dir}")

# -------------------------------------------------------------
# function to get subject of a message

def GetSubject(service, msg_id):
    message = service.users().messages().get(userId="me", id=msg_id).execute()
    for header in message['payload']['headers']:
        if header['name'] == 'Subject':
            return header['value']
    return None

# -------------------------------------------------------------
# authenticate

creds = authenticate()
service = build("gmail", "v1", credentials=creds)

# -------------------------------------------------------------
# get message ids with specific label

msg_ids = ( service.users().messages()
    .list(userId="me", labelIds=[label_id]).execute() )
msg_ids = [msg['id'] for msg in msg_ids['messages']]

print(f"{len(msg_ids)} messages found")

# -------------------------------------------------------------
# download attachments and move messages to trash

for id in msg_ids:
# id = msg_ids[0]

    DownloadAttachments(service, id)

    DownloadInlineImages(service, id)

    subject = GetSubject(service, id)

    service.users().messages().trash(userId="me", id=id).execute()
    print(f"Message '{subject}' moved to trash")