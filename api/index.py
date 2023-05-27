from telegram import Update
from telegram.ext import Updater
from flask import Flask, request, render_template
import os
from bot.telegram_bot import setup_handlers

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), updater.bot)
    dispatcher.process_update(update)
    return "OK"


@app.route("/")
def index():
    return render_template("app.html")


setup_handlers(dispatcher)  # Call function to set up bot handlers

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
