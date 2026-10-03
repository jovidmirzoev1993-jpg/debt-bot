import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder
from handlers import get_handlers

TOKEN = os.environ.get("BOT_TOKEN")
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running"

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    for h in get_handlers():
        app.add_handler(h)
    app.run_polling()

if __name__ == "__main__":
    t = threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))))
    t.start()
    run_bot()
