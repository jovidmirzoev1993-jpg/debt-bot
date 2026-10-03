from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

debts = {}

def get_keyboard():
    kb = [["/qarz", "/hisob"]]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот кор мекунад! Нависед: Али 200", reply_markup=get_keyboard())

async def show_qarz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not debts:
        await update.message.reply_text("Карз нест", reply_markup=get_keyboard())
        return
    t = ""
    for k,v in debts.items():
        t += f"{k}: {v}\n"
    await update.message.reply_text(t, reply_markup=get_keyboard())

async def show_hisob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Хамаги: {sum(debts.values())}", reply_markup=get_keyboard())

async def reset_debts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    debts.clear()
    await update.message.reply_text("Тоза шуд", reply_markup=get_keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower().startswith("нест кун"):
        name = text[8:].strip()
        if name in debts:
            del debts[name]
            await update.message.reply_text(f"{name} нест шуд", reply_markup=get_keyboard())
        return
    parts = text.split()
    if len(parts) >= 2 and parts[-1].lstrip("-").isdigit():
        name = " ".join(parts[:-1])
        amount = int(parts[-1])
        if amount < 0:
            if name in debts:
                debts[name] += amount
                if debts[name] <= 0:
                    del debts[name]
                    await update.message.reply_text(f"{name} баста шуд", reply_markup=get_keyboard())
                else:
                    await update.message.reply_text(f"{name} боки {debts[name]}", reply_markup=get_keyboard())
        else:
            debts[name] = debts.get(name, 0) + amount
            await update.message.reply_text(f"{name} = {debts[name]}", reply_markup=get_keyboard())

def get_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("qarz", show_qarz),
        CommandHandler("hisob", show_hisob),
        CommandHandler("toza", reset_debts),
        CommandHandler("reset", reset_debts),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    ]
