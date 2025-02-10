import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from handlers import (
    start_command,
    help_command,
    clear_command,
    generate_image_command,
    speak_command,
    message_handler
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_bot():
    """Start the bot"""
    logger.info("Starting bot...")
    try:
        application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("clear", clear_command))
        application.add_handler(CommandHandler("speak", speak_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        logger.info("Bot configuration loaded")
        logger.info(f"Using {Config.AI_MODEL} for chat generation")

        # Start the bot with polling
        application.run_polling()

    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)

if __name__ == "__main__":
    if Config.validate():
        run_bot()
    else:
        logger.error("Invalid configuration. Please check your config.py file.")