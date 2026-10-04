from telegram.ext import *
import json, os

FILE = "debts.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save(d):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

async def start(u,c):
    await u.message.reply_text("ВЕРСИЯ 2.0 - Нависед: Аббос 500")

async def qarz(u,c):
    debts = load()
    if not debts:
        await u.message.reply_text("Холӣ аст")
        return
    t="\n".join([f"{k}: {v['s'] if isinstance(v,dict) else v}" for k,v in debts.items()])
    await u.message.reply_text(t)

async def toza(u,c):
    await u.message.reply_text("Барои тоза кардан нависед: ха")

async def text_handler(u,c):
    m=u.message.text.strip()
    low=m.lower()

    # 1. Тоза кардан
    if low=="ха":
        save({})
        await u.message.reply_text("ВЕРСИЯ 2.0 - Тоза шуд")
        return

    debts = load() # каждый раз загружаем свежий файл!

    # 2. Нест кардан
    if low.startswith("нест"):
        s=low.replace("нест кун","").replace("нест","").strip()
        if not s:
            await u.message.reply_text("Кого нест? Нависед: Нест Аббос")
            return

        # ищем
        found=[k for k in debts.keys() if s in k.lower() or k.lower() in s]

        if not found:
            await u.message.reply_text(f"ВЕРСИЯ 2.0 - Ёфт нашуд '{s}'. Дар база: {list(debts.keys())}")
            return

        for k in found:
            del debts[k]
        save(debts)
        await u.message.reply_text(f"ВЕРСИЯ 2.0 - ✅ Нест шуд: {', '.join(found)}")
        return

    # 3. Добавить
    try:
        p=m.split()
        idx=-1
        val=0
        for i,x in enumerate(p):
            if x.isdigit():
                idx=i
                val=int(x)
                break
        if idx==-1:
            raise ValueError

        name=" ".join(p[:idx]).strip()
        if not name:
            raise ValueError

        debts[name]={"s":val}
        save(debts)
        await u.message.reply_text(f"ВЕРСИЯ 2.0 - Қарзи {val} барои {name} сабт шуд")
    except:
        await u.message.reply_text("ВЕРСИЯ 2.0 - Нодуруст. Мисол: Аббос 500")

def get_handlers():
    return [
        CommandHandler("start",start),
        CommandHandler("qarz",qarz),
        CommandHandler("toza",toza),
        MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler)
    ]
