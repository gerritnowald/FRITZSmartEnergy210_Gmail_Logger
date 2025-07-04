from googleapiclient.discovery import build

import base64

from authentication.auth import authenticate

# -------------------------------------------------------------
# user input

label_id = "Label_231893078114603930"

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
            path = './data/' + part['filename']

            with open(path, 'wb') as f:
                f.write(file_data)
                print(f"Downloaded {part['filename']} to ./data/")

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
# id = msg_ids[-1]

    DownloadAttachments(service, id)

# service.users().messages().trash(userId="me", id=id).execute()
# print(f"Message {id} moved to trash")