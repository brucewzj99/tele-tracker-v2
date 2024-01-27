import logging
from telegram.ext import Updater
import os
from bot.telegram_bot import setup_handlers

# Enable logging and set the file to write logs to
log_file = "telegram_bot.log"
logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TEST_TOKEN")
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

setup_handlers(dispatcher)

if __name__ == "__main__":
    updater.start_polling()
    print(f"# Bot is running at @{updater.bot.get_me().username} #")
    updater.idle()
