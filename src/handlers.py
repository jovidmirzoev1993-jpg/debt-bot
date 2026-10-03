from telegram import Update
from telegram.ext import *
import datetime, json, os

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
        json.dump(d, f, ensure_ascii=False)

debts = load()

def now():
    return str(datetime.date.today())

async def r(u,t):
    await u.message.reply_text(t)

async def start(u,c):
    await r(u,"📒 Қарз дафтар\n\nНависед: Али 200\n\n/qarz - рӯйхат\n/hisob - ҳисоб\n/toza - тоза кардан\nнест кун Али - нест кардан")

async def qarz(u,c):
    if not debts:
        await r(u,"Рӯйхат холӣ")
        return
    s="📒 Дафтар:\n"
    j=0
    for k,v in debts.items():
        j+=1
        s+=f"{j}. {k} - {v['s']} сомонӣ - {v['d']}\n"
    tot=sum(x['s'] for x in debts.values())
    s+=f"\n💰 Ҷамъ: {tot}\n👥 {j} нафар"
    await r(u,s)

async def hisob(u,c):
    tot=sum(x['s'] for x in debts.values())
    await r(u,f"💰 Ҷамъи қарзҳо: {tot} сомонӣ\n👥 {len(debts)} нафар")

async def toza(u,c):
    debts.clear()
    save(debts)
    await r(u,"✅ Ҳама тоза карда шуд")

async def do_del(u,nm):
    if not nm:
        await r(u,"Номро нависед: нест кун Аббос")
        return
    for k in list(debts.keys()):
        if k.lower() == nm.lower():
            del debts[k]
            save(debts)
            await r(u,f"✅ {k} нест карда шуд!")
            return
    await r(u,f"Мизоҷ '{nm}' ёфт нашуд. /qarz -ро санҷед")

async def txt(u,c):
    m=u.message.text.strip()
    l=m.lower()

    if l.startswith("нест кун"):
        nm = m[8:].strip()
        # если написали "нест кун" и пробел 8 символов, но для безопасности:
        if len(m) > 8:
            nm = m[8:].strip()
        else:
            nm = ""
        await do_del(u,nm)
        return
    if l.startswith("нест"):
        nm = m[4:].strip()
        await do_del(u,nm)
        return

    try:
        a,b=m.rsplit(' ',1)
        n=int(b)
        # сохраняем имя как написал пользователь, но с большой буквы
        real_name = a.strip()
        if not real_name:
            raise ValueError
        # ищем существующий ключ без учета регистра
        found_key = None
        for k in debts.keys():
            if k.lower() == real_name.lower():
                found_key = k
                break

        key_to_use = found_key if found_key else real_name

        if key_to_use in debts:
            debts[key_to_use]['s']+=n
            debts[key_to_use]['d']=now()
        else:
            debts[key_to_use]={'s':n,'d':now()}

        if debts[key_to_use]['s']<=0:
            del debts[key_to_use]
            save(debts)
            await r(u,f"✅ {key_to_use} тоза шуд - қарзаш тамом")
        else:
            save(debts)
            ba=debts[key_to_use]['s']
            await r(u,f"✅ Сабт шуд: {key_to_use}\n💰 Бақия: {ba} сомонӣ")
    except:
        await r(u,"❌ Нависед: Али 200\nё: нест кун Али")

def get_handlers():
    return[
        CommandHandler("start",start),
        CommandHandler("qarz",qarz),
        CommandHandler("hisob",hisob),
        CommandHandler("toza",toza),
        MessageHandler(filters.TEXT & ~filters.COMMAND,txt)
    ]
