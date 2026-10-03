import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder
from handlers import handle_message, handle_callback

BOT_TOKEN = os.getenv("BOT_TOKEN")
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is alive!"

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(handle_message)
    app.add_handler(handle_callback)
    print("Bot started polling...")
    app.run_polling()

threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))), daemon=True).start()
run_bot()
