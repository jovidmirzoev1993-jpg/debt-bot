import os, threading
from flask import Flask
from telegram.ext import ApplicationBuilder
from handlers import get_handlers, daily_check

TOKEN=os.environ.get("BOT_TOKEN")
flask_app=Flask(__name__)

@flask_app.route("/")
def home(): return "Bot is running"

def run_bot():
    app=ApplicationBuilder().token(TOKEN).build()
    for h in get_handlers():
        app.add_handler(h)
    # Ҳар рӯз соати 09:00 (ва ҳар 1 соат барои тест)
    # 3600 = ҳар соат санҷиш, 86400 = ҳар рӯз
    app.job_queue.run_repeating(daily_check, interval=3600, first=10)
    app.run_polling()

if __name__=="__main__":
    t=threading.Thread(target=lambda: flask_app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000))))
    t.start()
    run_bot()
