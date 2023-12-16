from telegram import Bot
import os
import bot.firestore_service as fs

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)


def send_new_feature_message(new_feature_message):
    users = fs.get_all_user_id()
    for user_id in users:
        bot.send_message(chat_id=user_id, text=new_feature_message)
    print("Message has been pushed to all users")
