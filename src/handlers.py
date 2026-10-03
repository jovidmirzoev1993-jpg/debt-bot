from telegram import Update
from telegram.ext import *

debts = {}

async def start(u,c):
    await u.message.reply_text("Напиши: Али 200\n/qarz - руйхат\nнест Аббос - удалить")

async def qarz(u,c):
    if not debts:
        await u.message.reply_text("Холи")
        return
    t=""
    for k,v in debts.items():
        t+=f"{k}: {v}\n"
    await u.message.reply_text(t)

async def txt(u,c):
    m=u.message.text.strip()
    # УДАЛИТЬ
    if m.lower().startswith("нест"):
        name=m[4:].strip()
        for k in list(debts.keys()):
            if k.lower()==name.lower():
                del debts[k]
                await u.message.reply_text(f"{k} удален!")
                return
        await u.message.reply_text(f"Нет такого: {name}. Есть: {', '.join(debts.keys())}")
        return
    # ДОБАВИТЬ
    try:
        a,b=m.rsplit(' ',1)
        debts[a.strip()]=int(b)
        await u.message.reply_text(f"{a} = {b}")
    except:
        await u.message.reply_text("Пиши: Али 200")

def get_handlers():
    return [CommandHandler("start",start),CommandHandler("qarz",qarz),MessageHandler(filters.TEXT & ~filters.COMMAND, txt)]
