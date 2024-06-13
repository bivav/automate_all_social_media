from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
import telegram.ext.filters as filters
import logging
import os

API_TOKEN = os.getenv('TELEGRAM_API_KEY')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Use /set <seconds> to set a timer')

async def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

def main():
    """Start the bot."""
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()