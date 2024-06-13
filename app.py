import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API credentials from environment variables
api_id = int(os.getenv('TELEGRAM_API_ID'))
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

# Store messages in a list
messages = []

@client.on(events.NewMessage)
async def my_event_handler(event):
    sender = await event.get_sender()
    sender_name = sender.username or sender.first_name
    message_info = f"Sender: {sender_name}\nMessage: {event.message.message}\n"
    messages.append(message_info)
    print(f"Captured message: {message_info}")

async def main():
    # Connect to the client
    await client.start(phone_number)

    # Keep the client running to listen for new messages
    print("Client is running. Listening for new messages...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())