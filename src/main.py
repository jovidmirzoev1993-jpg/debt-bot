import sys
import os

# Фикс для двойной папки src/src
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import threading
from flask import Flask
from telegram.ext import ApplicationBuilder
from handlers import handle_message

BOT_TOKEN = os.getenv("BOT_TOKEN")

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is alive!"

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(handle_message)
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
