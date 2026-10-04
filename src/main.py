import os, json, asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавь в Render -> Environment")

DATA_FILE = "data/debts.json"
os.makedirs("data", exist_ok=True)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}
def save(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

@dp.message(Command("start"))
async def start(m): await m.answer("✅ БОТ V3.2 РАБОТАЕТ\n\nАббос 500 - добавить\nНест Аббос - удалить\n/qarz - список\n/hisob - итог")

@dp.message(Command("qarz"))
async def qarz(m):
    data=load()
    if not data: await m.answer("📭 Рӯйхат холӣ аст."); return
    txt="📒 Рӯйхати қарзҳо:\n"
    for k,v in data.items(): txt+=f"• {k}: {v}\n"
    await m.answer(txt)

@dp.message(Command("hisob"))
async def hisob(m):
    data=load()
    total=sum(data.values()) if data else 0
    await m.answer(f"💰 Хисоби умумӣ: {total} сомонӣ\n👥 {len(data)} нафар")

@dp.message()
async def all_msg(m: types.Message):
    text=m.text.strip()
    data=load()
    low=text.lower()

    if "хисоби умумӣ" in low or low=="/hisob":
        total=sum(data.values()) if data else 0
        if not data: await m.answer("📭 Ҳоло қарз нест. Ҷамъ: 0"); return
        await m.answer(f"💰 Хисоби умумӣ: {total} сомонӣ"); return

    if "рӯйхати қарзҳо" in low or low=="/qarz":
        if not data: await m.answer("📭 Рӯйхат холӣ аст."); return
        txt="📒 Рӯйхати қарзҳо:\n"
        for k,v in data.items(): txt+=f"• {k}: {v}\n"
        await m.answer(txt); return

    if low.startswith("нест "):
        name=text[5:].strip()
        found=None
        for k in data.keys():
            if k.lower()==name.lower(): found=k; break
        if found: del data[found]; save(data); await m.answer(f"✅ {found} нест шуд!")
        else: await m.answer(f"Ёфт нашуд: {name}. Дар база: {list(data.keys())}")
        return

    parts=text.rsplit(" ",1)
    if len(parts)==2 and parts[1].isdigit():
        name,summ=parts[0].strip(),int(parts[1])
        data[name]=data.get(name,0)+summ; save(data)
        await m.answer(f"✅ {name} +{summ}. Бақия: {data[name]}")
        return

# Веб-сервер для Render
async def handle(request): return web.Response(text="V3.2 OK - Bot is running")

async def main():
    app=web.Application(); app.add_routes([web.get('/', handle)])
    runner=web.AppRunner(app); await runner.setup()
    site=web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000)))
    await site.start()
    print("Web server started")
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
