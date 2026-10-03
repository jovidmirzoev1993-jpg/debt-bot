from telegram.ext import *
import json, os

FILE = "debts.json"
def load():
    if os.path.exists(FILE):
        try:
            import json
            with open(FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def save(d):
    with open(FILE, "w", encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False)
debts=load()

async def start(u,c): await u.message.reply_text("ВЕРСИЯ 2.0 - Нависед: Аббос 500")
async def qarz(u,c):
    if not debts: await u.message.reply_text("Холӣ аст"); return
    t="\n".join([f"{k}: {v['s'] if isinstance(v,dict) else v}" for k,v in debts.items()])
    await u.message.reply_text(t)
async def toza(u,c): await u.message.reply_text("ХА нависед")

async def text_handler(u,c):
    global debts
    m=u.message.text.strip(); low=m.lower()
    if low=="ха":
        debts={}; save(debts); await u.message.reply_text("ВЕРСИЯ 2.0 - Тоза шуд"); return
    if low.startswith("нест"):
        s=low.replace("нест кун","").replace("нест","").strip()
        found=[k for k in debts.keys() if s in k.lower()]
        if not found: await u.message.reply_text(f"ВЕРСИЯ 2.0 - Ёфт нашуд. Дар база: {list(debts.keys())}"); return
        for k in found: del debts[k]
        save(debts); await u.message.reply_text(f"ВЕРСИЯ 2.0 - ✅ Нест шуд: {', '.join(found)}"); return
    try:
        p=m.split(); idx=-1; val=0
        for i,x in enumerate(p):
            if x.isdigit(): idx=i; val=int(x); break
        if idx==-1: raise ValueError
        name=" ".join(p[:idx])
        debts[name]={"s":val}; save(debts)
        await u.message.reply_text(f"ВЕРСИЯ 2.0 - Қарзи {val} барои {name} сабт шуд")
    except: await u.message.reply_text("ВЕРСИЯ 2.0 - Нодуруст")

def get_handlers():
    return [CommandHandler("start",start),CommandHandler("qarz",qarz),CommandHandler("toza",toza),MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler)]
