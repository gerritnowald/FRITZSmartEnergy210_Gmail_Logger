import base64

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth import authenticate


class GmailApi:
    
    def __init__(self):
        creds = authenticate()
        self.service = build("gmail", "v1", credentials=creds)

    
    def find_emails(self, sender: str):
        request = (
            self.service.users()
            .messages()
            .list(userId="me", q=f"from:{sender}", maxResults=200)
        )

        result = self._execute_request(request)
        try:
            messages = result["messages"]
            print(f"Retrieved messages matching the '{sender}' query: {len(messages)}")
        except KeyError:
            print(f"No messages found for the sender '{sender}'")
            messages = []

        return messages

    
    def get_email(self, email_id: str):

        request = self.service.users().messages().get(userId="me", id=email_id)
        result  = self._execute_request(request)

        content = result["payload"]["parts"][0]["body"]["data"]
        content = content.replace("-", "+").replace("_", "/")
        decoded = base64.b64decode(content).decode("utf-8")

        print(f"Retrieved email with email_id={email_id}: {result}")

        return decoded
    

    def list_labels(self):
        
        request = self.service.users().labels().list(userId="me")
        results = self._execute_request(request)

        labels  = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return
        print("Labels:")
        for label in labels:
            print(label["name"])

        print(f"Retrieved {len(labels)} labels.")

        return labels

    
    @staticmethod
    def _execute_request(request):
        try:
            return request.execute()
        except HttpError as e:
            print(f"An error occurred: {e}")
            raise RuntimeError(e)
