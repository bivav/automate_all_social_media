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
api_id = int(os.getenv('TELEGRAM_API_ID'))
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
email_address = os.getenv('EMAIL_ADDRESS')
email_password = os.getenv('EMAIL_PASSWORD')
recipient_email = os.getenv('RECIPIENT_EMAIL')

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

# Store messages in a list
messages = []
sent_message_ids = set()

# Load sent message IDs from file
if os.path.exists('sent_message_ids.txt'):
    with open('sent_message_ids.txt', 'r') as f:
        sent_message_ids = set(f.read().splitlines())

@client.on(events.NewMessage)
async def my_event_handler(event):
    message_id = event.message.id
    if str(message_id) not in sent_message_ids:
        sender = await event.get_sender()
        sender_name = sender.username or sender.first_name
        message_info = f"Sender: {sender_name}\nMessage: {event.message.message}\n"
        messages.append((message_id, message_info))
        print(f"Captured message: {message_info}")

def send_email():
    """Send the collected messages via email."""
    if not messages:
        return

    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = 'Collected Messages'

    body = "\n\n".join([msg_info for _, msg_info in messages])
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, recipient_email, msg.as_string())
        print("Email sent successfully.")
        
        # Record the IDs of sent messages
        with open('sent_message_ids.txt', 'a') as f:
            for message_id, _ in messages:
                f.write(f"{message_id}\n")

        # Clear messages after sending
        messages.clear()
    except Exception as e:
        print(f"Failed to send email: {e}")

# Schedule the email sending function to run every 30 minutes
schedule.every(1).minutes.do(send_email)

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

if __name__ == '__main__':
    client.loop.run_until_complete(main())