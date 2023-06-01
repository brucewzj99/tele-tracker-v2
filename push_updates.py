import os
from telegram import Bot
import bot.updates as up

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)

# msg = "Msg here to push"
# up.send_new_feature_message(msg)

