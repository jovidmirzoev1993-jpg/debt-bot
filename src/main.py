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
    p = os.environ.get("PORT", "10000")
    port = int(p)
    flask_app.run(host="0.0.0.0", port=port)

def run_bot():
    b = ApplicationBuilder()
    b = b.token(BOT_TOKEN)
    app = b.build()
    hs = get_handlers()
    for h in hs:
        app.add_handler(h)
    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    run_bot()
