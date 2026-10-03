import os
import sqlite3
import logging
import threading
from decimal import Decimal
from datetime import datetime
from flask import Flask
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_PATH = "debt.db"

# Маленький сайт для Render чтобы не падал
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

logging.basicConfig(level=logging.INFO)
def fmt(a: Decimal): return f"{a:.0f}" if a == int(a) else f"{a:.2f}"
def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS debts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, amount TEXT, comment TEXT, created_at TEXT)")
        conn.commit()
init_db()
def get_keyboard():
    return ReplyKeyboardMarkup([["Spisok dolgov"], ["Dobavit dolg", "Dolgi mne"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Privet! Ya bot dlya ucheta dolgov.\n\nNapishi: Ali 5000 za obed", reply_markup=get_keyboard())

async def add_debt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith("/") or text in ["Spisok dolgov", "Dobavit dolg", "Dolgi mne"]: return
    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text("Napishi: Imya Summa [komment]"); return
    try:
        name = parts[0]; amount = Decimal(parts[1].replace(",", "."))
        comment = " ".join(parts[2:]) if len(parts) > 2 else ""
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO debts (user_id, name, amount, comment, created_at) VALUES (?,?,?,?,?)", (update.effective_user.id, name, str(amount), comment, datetime.now().isoformat()))
            conn.commit()
        await update.message.reply_text(f"Zapisal: {name} - {fmt(amount)} {comment}")
    except Exception as e:
        await update.message.reply_text(f"Oshibka: {e}")

async def list_debts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor(); c.execute("SELECT name, amount, comment FROM debts WHERE user_id=? ORDER BY id DESC", (update.effective_user.id,)); rows = c.fetchall()
    if not rows: await update.message.reply_text("Dolgov poka net."); return
    total = sum(Decimal(r[1]) for r in rows); msg = "Tvoi dolgi:\n\n"
    for name, amount, comment in rows[:50]: msg += f"- {name} - {fmt(Decimal(amount))} {comment}\n"
    msg += f"\nItogo: {fmt(total)}"; await update.message.reply_text(msg)

async def debts_to_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Skoro budet!")
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN ne zadan!")
    threading.Thread(target=run_flask, daemon=True).start()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("list", list_debts))
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
