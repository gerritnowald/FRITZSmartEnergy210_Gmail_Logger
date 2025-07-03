import base64

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth.auth import authenticate


class GmailApi:
    def __init__(self):
        creds = authenticate()
        self.service = build("gmail", "v1", credentials=creds)

    def find_emails(self, sender: str):
        print("\n=============== Find Emails: start ===============")
        request = (
            self.service.users()
            .messages()
            .list(userId="me", q=f"from:{sender}", maxResults=200)
        )

        result = self._execute_request(request)
        try:
            messages = result["messages"]
            print(f"Retrieved messages matching the '{sender}' query: {messages}")
        except KeyError:
            print(f"No messages found for the sender '{sender}'")
            messages = []

        print("=============== Find Emails: end ===============")

        return messages

    def get_email(self, email_id: str):
        print("\n=============== Get Email: start ===============")

        request = self.service.users().messages().get(userId="me", id=email_id)
        result = self._execute_request(request)
        content = result["payload"]["parts"][0]["body"]["data"]
        content = content.replace("-", "+").replace("_", "/")
        decoded = base64.b64decode(content).decode("utf-8")

        print(f"Retrieved email with email_id={email_id}: {result}")
        print("=============== Get Email: end ===============")

        return decoded

    @staticmethod
    def _execute_request(request):
        try:
            return request.execute()
        except HttpError as e:
            print(f"An error occurred: {e}")
            raise RuntimeError(e)
