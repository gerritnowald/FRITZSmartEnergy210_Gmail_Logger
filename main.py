from client import GmailApi


def main():
    client = GmailApi()

    client.list_labels()

    sender = "hannahritchie@substack.com"    # either email or sender name
    emails = client.find_emails(sender)
    email_ids = [email["id"] for email in emails]

    contents = [client.get_email(email_id) for email_id in email_ids]
    print(f"Content of the emails matching sender '{sender}':")
    for content in contents:
        print(content)


if __name__ == "__main__":
    main()
