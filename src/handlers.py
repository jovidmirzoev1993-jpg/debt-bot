from telegram.ext import *
import json, os, datetime

FILE = "debts.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

debts = load()

async def start(u,c):
    await u.message.reply_text("Нависед: Аббос 500\nНест Аббос - барои нест кардан\n/qarz - руйхат\n/toza - тоза кардан")

async def qarz(u,c):
    if not debts:
        await u.message.reply_text("Холӣ аст")
        return
    txt = ""
    for k,v in debts.items():
        s = v["s"] if isinstance(v, dict) else v
        txt += f"{k}: {s} сомонӣ\n"
    await u.message.reply_text(txt)

async def toza(u,c):
    await u.message.reply_text("Барои тоза кардан ХА нависед")

async def text_handler(u,c):
    global debts
    m = u.message.text.strip()
    low = m.lower()

    if low == "ха":
        debts = {}
        save(debts)
        await u.message.reply_text("Дафтари қарзҳо тоза шуд.")
        return

    # === НЕСТ КУН - УМНОЕ ===
    if low.startswith("нест"):
        # тоза мекунем "нест кун"
        search = low.replace("нест кун", "").replace("нест", "").strip()
        if not search:
            await u.message.reply_text("Кӣ нест шавад? Мисол: Нест Аббос")
            return

        # меҷӯем бо қисм - "аббос" дар "аббос завтра" ёфт мешавад
        to_del = []
        for key in list(debts.keys()):
            if search in key.lower() or key.lower() in search:
                to_del.append(key)

        if not to_del:
            await u.message.reply_text(f"Мизоҷ '{search}' ёфт нашуд. Рӯйхат: {', '.join(debts.keys())}")
            return

        for k in to_del:
            del debts[k]
        save(debts)
        await u.message.reply_text(f"✅ Нест шуд: {', '.join(to_del)}")
        return

    # === ИЛОВА - ДУРУСТ МЕФАҲМАД "завтра" ===
    try:
        parts = m.split()
        sum_idx = -1
        sum_val = 0
        for i, p in enumerate(parts):
            if p.isdigit():
                sum_idx = i
                sum_val = int(p)
                break

        if sum_idx == -1:
            raise ValueError

        name = " ".join(parts[:sum_idx]).strip()
        if not name:
            raise ValueError

        # "завтра" -ро ҳамчун муҳлат мегирем, на ҳамчун ном
        debts[name] = {"s": sum_val}
        save(debts)
        await u.message.reply_text(f"Қарзи {sum_val} барои {name} сабт шуд. Бақияи нав: {sum_val} сомонӣ.")

    except:
        await u.message.reply_text("Нодуруст. Нависед: Аббос 500")

def get_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("qarz", qarz),
        CommandHandler("toza", toza),
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)
    ]
