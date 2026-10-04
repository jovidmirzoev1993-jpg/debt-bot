import os, json, asyncio
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data/debts.json"
os.makedirs("data", exist_ok=True)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Конверт старого формата (просто число) в новый (с датой)
            for k,v in list(data.items()):
                if isinstance(v, int):
                    data[k] = {"amount": v, "date": datetime.now().strftime("%d.%m.%Y"), "updated": datetime.now().strftime("%d.%m.%Y %H:%M")}
            return data
    except: return {}

def save(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

@dp.message(Command("start"))
async def start(m):
    await m.answer("✅ V3.3 - Бо санаҳо\n\nАббос 500\nНест Аббос\n/qarz\n/hisob")

@dp.message(Command("qarz"))
async def qarz(m):
    data=load()
    if not data: await m.answer("📭 Рӯйхат холӣ аст."); return
    txt="📒 Рӯйхати қарзҳо:\n"
    for k,v in data.items():
        amt = v["amount"] if isinstance(v, dict) else v
        date = v.get("date","") if isinstance(v, dict) else ""
        txt+=f"• {k}: {amt} сомонӣ - {date}\n"
    await m.answer(txt)

@dp.message(Command("hisob"))
async def hisob(m):
    data=load()
    if not data: await m.answer("💰 Хисоби умумӣ:\nҶамъ: 0 сомонӣ\n📭 Қарз нест"); return
    total = sum(v["amount"] if isinstance(v, dict) else v for v in data.values())
    txt=f"💰 Хисоби умумӣ:\n"
    txt+=f"Ҷамъ: {total} сомонӣ\n"
    txt+=f"👥 {len(data)} нафар қарздор\n\n"
    for k,v in data.items():
        amt = v["amount"] if isinstance(v, dict) else v
        date = v.get("updated", v.get("date","")) if isinstance(v, dict) else ""
        txt+=f"• {k}: {amt} - {date}\n"
    await m.answer(txt)

@dp.message()
async def all_msg(m):
    text=m.text.strip()
    low=text.lower()
    data=load()

    if "хисоби умумӣ" in low or low=="/hisob":
        await hisob(m); return
    if "рӯйхати қарзҳо" in low or low=="/qarz":
        await qarz(m); return
    if "қарз додан" in low: await m.answer("Нависед: Аббос 500"); return
    if "баргашт кард" in low: await m.answer("Нависед: Нест Аббос"); return

    if low.startswith("нест "):
        name=text[5:].strip()
        found=None
        for k in data.keys():
            if k.lower()==name.lower(): found=k; break
        if found: del data[found]; save(data); await m.answer(f"✅ {found} нест шуд!")
        else: await m.answer(f"Ёфт нашуд: {name}")
        return

    parts=text.rsplit(" ",1)
    if len(parts)==2 and parts[1].isdigit():
        name,summ=parts[0].strip(),int(parts[1])
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        today = datetime.now().strftime("%d.%m.%Y")
        if name in data and isinstance(data[name], dict):
            data[name]["amount"] += summ
            data[name]["updated"] = now
        elif name in data:
            data[name] = {"amount": data[name]+summ, "date": today, "updated": now}
        else:
            data[name] = {"amount": summ, "date": today, "updated": now}
        save(data)
        amt = data[name]["amount"]
        await m.answer(f"✅ {name} +{summ}. Бақия: {amt} - {now}")
        return

async def handle(request): return web.Response(text="V3.3 OK")

async def main():
    app=web.Application(); app.add_routes([web.get('/', handle)])
    runner=web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__=="__main__": asyncio.run(main())
