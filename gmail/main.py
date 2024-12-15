from client import GmailApi


def main():
    client = GmailApi()

    sender = "your sender here: either email or sender name"
    emails = client.find_emails(sender)
    email_ids = [email["id"] for email in emails]
    contents = [client.get_email(email_id) for email_id in email_ids]

    print(f"Content of the emails matching sender '{sender}':")
    for content in contents:
        print(content)


if __name__ == "__main__":
    main()
