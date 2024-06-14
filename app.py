import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telethon import TelegramClient, events
from dotenv import load_dotenv
import schedule
import time

# Load environment variables from .env file
load_dotenv()

# Get the API credentials from environment variables
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
phone_number = os.getenv("TELEGRAM_PHONE_NUMBER")
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")

# Create the client and connect
client = TelegramClient("session_name", api_id, api_hash)

# Store messages in a list
messages = []
sent_message_ids = set()

# Load sent message IDs from file
if os.path.exists("sent_message_ids.txt"):
    with open("sent_message_ids.txt", "r") as f:
        sent_message_ids = set(f.read().splitlines())


@client.on(events.NewMessage)
async def my_event_handler(event):
    message_id = event.message.id
    sender = await event.get_sender()
    sender_name = sender.username or sender.first_name

    # Ignore messages from 'bivavraj'
    if sender_name == "bivavraj":
        return

    if str(message_id) not in sent_message_ids:
        message_info = (message_id, sender_name, event.message.message)
        messages.append(message_info)
        print(f"Captured message: {message_info}")


def send_email():
    """Send the collected messages via email."""
    if not messages:
        return

    # Group messages by sender
    grouped_messages = {}
    for message_id, sender_name, text in messages:
        if sender_name not in grouped_messages:
            grouped_messages[sender_name] = []
        grouped_messages[sender_name].append(text)

    # Create the MIMEMultipart object
    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = recipient_email
    msg["Subject"] = "Collected Messages"

    # Build the email body
    body = ""
    for sender, msgs in grouped_messages.items():
        body += f"Sender: {sender}\n"
        for msg_text in msgs:
            body += f"-> {msg_text}\n"
        body += "\n"

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, recipient_email, msg.as_string())
        print("Email sent successfully.")

        # Record the IDs of sent messages
        with open("sent_message_ids.txt", "a") as f:
            for message_id, _, _ in messages:
                f.write(f"{message_id}\n")

        # Clear messages after sending
        messages.clear()
    except Exception as e:
        print(f"Failed to send email: {e}")


# Schedule the email sending function to run every 15 seconds for testing
schedule.every(15).seconds.do(send_email)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


async def main():
    # Connect to the client
    await client.start(phone_number)

    # Start the schedule in a separate thread
    import threading

    threading.Thread(target=run_schedule, daemon=True).start()

    # Keep the client running to listen for new messages
    print("Client is running. Listening for new messages...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    client.loop.run_until_complete(main())
