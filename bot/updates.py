from telegram import Bot
import os
import bot.firebase as fb

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)


def send_new_feature_message(new_feature_message):
    users = fb.get_all_user_id()
    for user_id in users:
        bot.send_message(chat_id=user_id, text=new_feature_message)


def update_gsheet():
    sheet_ids = fb.get_all_sheet_id()
    for sheet_id in sheet_ids:
        pass  # gs.update_gsheet(sheet_id)