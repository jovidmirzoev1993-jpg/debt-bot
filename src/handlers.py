from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

# Хранилище долгов (пока в памяти)
debts = {}

def get_keyboard():
    keyboard = [
        ["+ Қарз додан", "✅ Баргашт кард"],
        ["📒 Рӯйхати қарзҳо (/qarz)", "💰 Ҳисоби умумӣ (/hisob)"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Ба дафтари қарзи мағоза хуш омадед.\n"
        "Аз тугмаҳо истифода баред ё нависед:\n"
        "Али Душанбе 200.\n"
        "Барои пардохт нависед: Али Душанбе -50 ё Али Душанбе баргашт 50.\n"
        "/qarz — дафтари қарз\n"
        "/hisob — ҳисоби умумӣ\n"
        "/toza ё /reset — тоза кардани қарзҳои шумо"
    )
    await update.message.reply_text(text, reply_markup=get_keyboard())

async def show_qarz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not debts:
        await update.message.reply_text("Ҳоло қарз нест.", reply_markup=get_keyboard())
        return
    msg = "📒 Рӯйхати қарзҳо:\n\n"
    for name, amount in debts.items():
        msg += f"{name}: {amount} сомонӣ\n"
    msg += "\nБарои нест кардан нависед: нест кун Али Душанбе"
    await update.message.reply_text(msg, reply_markup=get_keyboard())

async def show_hisob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = sum(debts.values())
    await update.message.reply_text(f"💰 Ҳамаи қарзҳо: {total} сомонӣ", reply_markup=get_keyboard())

async def reset_debts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    debts.clear()
    await update.message.reply_text("✅ Ҳама қарзҳо тоза карда шуданд.", reply_markup=get_keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Игнор кнопок
    if text in ["+ Қарз додан", "✅ Баргашт кард", "📒 Рӯйхати қарзҳо (/qarz)", "💰 Ҳисоби умумӣ (/hisob)"]:
        if "Рӯйхати" in text:
            await show_qarz(update, context)
        elif "Ҳисоби" in text:
            await show_hisob(update, context)
        elif "Қарз додан" in text:
            await update.message.reply_text("Ном ва маблағро нависед: Али Душанбе 200", reply_markup=get_keyboard())
        elif "Баргашт" in text:
            await update.message.reply_text("Барои баргашт нависед: Али Душанбе -50", reply_markup=get_keyboard())
        return

    # Нест кардан
    if text.lower().startswith("нест кун"):
        name = text[8:].strip()
        if name in debts:
            del debts[name]
            await update.message.reply_text(f"🗑️ {name} нест карда шуд.", reply_markup=get_keyboard())
        else:
            await update.message.reply_text(f"Мизоҷ {name} ёфт нашуд.", reply_markup=get_keyboard())
        return

    # Парсинг: "Али Душанбе 200" ё "Али Душанбе -50" ё "Али Душанбе баргашт 50"
    try:
        parts = text.split()
        if len(parts) < 2:
            return

        # маблағ охирин аст
