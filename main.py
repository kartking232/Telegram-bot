import logging
import time
from bot import run_bot
from config import Config
import os
import sys
from models import get_model_handler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot with continuous operation."""
    # Validate configuration
    if not Config.TELEGRAM_TOKEN:
        logger.error("Telegram token not found!")
        return

    while True:  # Continuous operation loop
        try:
            # Initialize model handler first to catch any model-related errors
            logger.info(f"Initializing {Config.AI_MODEL} model...")
            model_handler = get_model_handler(Config.AI_MODEL)
            logger.info(f"Successfully initialized {Config.AI_MODEL} model")

            # Run the bot
            run_bot()
        except Exception as e:
            logger.error(f"Error during operation: {e}", exc_info=True)
            logger.info("Waiting 10 seconds before restart...")
            time.sleep(10)  # Wait before retrying to avoid rapid restarts
        finally:
            logger.info("Bot stopped. Restarting...")

if __name__ == '__main__':
    # Check if there's a PID file
    pid_file = "bot.pid"

    # If PID file exists, check if the process is still running
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            old_pid = int(f.read().strip())
        try:
            # Check if process exists
            os.kill(old_pid, 0)
            logger.error("Bot is already running! Please stop the existing instance first.")
            sys.exit(1)
        except OSError:
            # Process is not running, we can remove the PID file
            os.remove(pid_file)

    # Write current PID to file
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

    try:
        main()
    finally:
        # Clean up PID file when the bot exits
        if os.path.exists(pid_file):
            os.remove(pid_file)