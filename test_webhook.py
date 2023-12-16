from telegram import Update
from telegram.ext import Updater
from flask import Flask, request
import os
from bot.telegram_bot import setup_handlers
from pyngrok import ngrok

TOKEN = os.environ.get("TEST_TOKEN")
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
    return "Bot is running!"


setup_handlers(dispatcher)

if __name__ == "__main__":
    public_url = ngrok.connect(5000, "http").public_url
    updater.bot.set_webhook(url=f"{public_url}/webhook")
    print("#" * 50)
    print(f"# Bot is running at @{updater.bot.get_me().username} #")
    print("#" * 50)
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True,
        use_reloader=False,
    )
