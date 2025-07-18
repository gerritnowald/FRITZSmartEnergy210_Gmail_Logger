from googleapiclient.discovery import build

from authentication.auth import authenticate

# -------------------------------------------------------------
# authenticate

creds = authenticate()
service = build("gmail", "v1", credentials=creds)

# -------------------------------------------------------------
# get labels

labels = service.users().labels().list(userId="me").execute()

# -------------------------------------------------------------
# print label names and ids

for label in labels['labels']:
    print(f"{label['name']} : {label['id']}")