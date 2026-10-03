import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from handlers import handle_message, list_debts, start

BOT_TOKEN = os.getenv("BOT_TOKEN")

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is alive!"

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_debts))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    # Бота запускаем в фоне
    threading.Thread(target=run_bot).start()
    # А Flask в главном потоке — так Render не падает
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)
