import os, json, threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")
FILE = "debts.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save(d):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

flask_app = Flask(__name__)
@flask_app.route("/")
def home(): return "Bot is running V2"

async def start(u,c):
    await u.message.reply_text("ВЕРСИЯ 2.0 - Нависед: Аббос 500")

async def qarz(u,c):
    debts = load()
    if not debts:
        await u.message.reply_text("Холӣ аст")
        return
    t="\n".join([f"{k}: {v.get('s',v) if isinstance(v,dict) else v}" for k,v in debts.items()])
    await u.message.reply_text(t)

async def toza(u,c):
    await u.message.reply_text("Барои тоза кардан ха нависед")

async def text_handler(u,c):
    m=u.message.text.strip()
    low=m.lower()
    if low=="ха":
        save({})
        await u.message.reply_text("ВЕРСИЯ 2.0 - Тоза шуд")
        return

    debts = load()

    if low.startswith("нест"):
        s=low.replace("нест кун","").replace("нест","").strip()
        if not s:
            await u.message.reply_text("Кого? Мисол: Нест Аббос")
            return
        found=[k for k in debts.keys() if s in k.lower()]
        if not found:
            await u.message.reply_text(f"Ёфт нашуд '{s}'. Дар база: {list(debts.keys())}")
            return
        for k in found: del debts[k]
        save(debts)
        await u.message.reply_text(f"✅ Нест шуд: {', '.join(found)}")
        return

    try:
        p=m.split()
        idx=-1
        for i,x in enumerate(p):
            if x.isdigit():
                idx=i; val=int(x); break
        if idx==-1: raise ValueError
        name=" ".join(p[:idx]).strip()
        if not name: raise ValueError
        debts[name]={"s":val}
        save(debts)
        await u.message.reply_text(f"✅ Сабт шуд: {name} - {val}")
    except:
        await u.message.reply_text("Мисол: Аббос 500 ё Нест Аббос")

def run_bot():
    app=ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("qarz",qarz))
    app.add_handler(CommandHandler("toza",toza))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()

if __name__=="__main__":
    t=threading.Thread(target=lambda: flask_app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000))))
    t.start()
    run_bot()
