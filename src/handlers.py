from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes

async def handle_message_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Получил: {text}\n\nБот работает! Тут будет логика долгов.")

handle_message = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_func)
