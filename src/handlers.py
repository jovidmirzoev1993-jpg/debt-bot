import json, os, datetime
from telegram import Update
from telegram.ext import *

FILE = "debts.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(debts, f, ensure_ascii=False, indent=2)

debts = load()

def now():
    return str(datetime.date.today())

async def r(u, t):
    await u.message.reply_text(t)

async def start(u, c):
    await r(u, "📒 Қарз дафтар\n\nНависед: Али 200\n/qarz - рӯйхат\n/hisob - ҳисоб\nнест кун Али - нест кардан")

async def qarz(u, c):
    if not debts:
        await r(u, "Рӯйхат холӣ")
        return
    s = "📒 Дафтар:\n"
    tot = 0
    for i, (k, v) in enumerate(debts.items(), 1):
        s += f"{i}. {k} - {v['s']} - {v['d']}\n"
        tot += v['s']
    s += f"\n💰 Ҷамъ: {tot} | {len(debts)} нафар"
    await r(u, s)

async def hisob(u, c):
    tot = sum(x['s'] for x in debts.values())
    await r(u, f"💰 Ҷамъ: {tot} сомонӣ")

async def toza(u, c):
    debts.clear()
    save()
    await r(u, "✅ Ҳама тоза шуд")

async def do_del(u, nm_raw):
    nm = nm_raw.strip().lower()
    if not nm:
        await r(u, "Номро нависед: нест кун Аббос")
        return
    for k in list(debts.keys()):
        if k.strip().lower() == nm:
            del debts[k]
            save()
            await r(u, f"✅ {k} нест карда шуд!")
            return
    # Диагностика - покажет что есть в базе
    if debts:
        await r(u, f"Мизоҷ '{nm_raw}' ёфт нашуд.\nДорем: {', '.join(debts.keys())}\nНависед точно: нест кун {list(debts.keys())[0]}")
    else:
        await r(u, "Рӯйхат холӣ, нест кардани чизе нест")

async def txt(u, c):
    m = u.message.text.strip()
    l = m.lower()
    if l.startswith("нест кун"):
        nm = m[8:].strip() if len(m) > 8 else ""
        await do_del(u, nm)
        return
    if l.startswith("нест"):
        nm = m[4:].strip() if len(m) > 4 else ""
        await do_del(u, nm)
        return
    try:
        a, b = m.rsplit(' ', 1)
        n = int(b)
        a = a.strip()
        if not a:
            raise ValueError
        found = None
        for k in debts:
            if k.lower() == a.lower():
                found = k
                break
        key = found if found else a
        if key in debts:
            debts[key]['s'] += n
            debts[key]['d'] = now()
        else:
            debts[key] = {'s': n, 'd': now()}
        if debts[key]['s'] <= 0:
            del debts[key]
            save()
            await r(u, f"✅ {key} тоза шуд")
        else:
            save()
            await r(u, f"✅ {key} - {debts[key]['s']} сомонӣ (Бақия: {debts[key]['s']})")
    except:
        await r(u, "❌ Нависед: Али 200\nё: нест кун Али")

def get_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("qarz", qarz),
        CommandHandler("hisob", hisob),
        CommandHandler("toza", toza),
        MessageHandler(filters.TEXT & ~filters.COMMAND, txt)
    ]
