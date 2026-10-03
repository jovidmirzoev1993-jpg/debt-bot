import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder
from handlers import get_handlers

BOT_TOKEN = os.getenv("BOT_TOKEN")

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    for h in get_handlers():
        app.add_handler(h)
    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
