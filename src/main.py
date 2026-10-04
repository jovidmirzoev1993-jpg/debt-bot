import asyncio
import os
import logging
import json
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DATA_FILE = "debts.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("ВЕРСИЯ 3.0 ИСПРАВЛЕНО\n\nАббос 500 - карз додан\nНест Аббос - нест кардан\n/qarz")

@dp.message(Command("qarz", "qarzdor", "hisob"))
async def show(m: types.Message):
    data = load_data()
    uid = str(m.from_user.id)
    user_debts = data.get(uid, {})
    if not user_debts:
        await m.answer("Холист")
        return
    txt = ""
    total = 0
    for name, amount in user_debts.items():
        txt += f"{name} - {amount}\n"
        total += amount
    await m.answer(txt + f"\nЧамъ: {total}")

@dp.message()
async def all_messages(m: types.Message):
    text = m.text.strip() if m.text else ""
    if not text:
        return
    low = text.lower()
    data = load_data()
    uid = str(m.from_user.id)
    if uid not in data:
        data[uid] = {}

    # НЕСТ - ПРОВЕРКА ПЕРВОЙ
    if low.startswith("нест "):
        name_to_del = text[5:].strip()
        # ищем без учета регистра
        found = None
        for k in data[uid].keys():
            if k.lower() == name_to_del.lower():
                found = k
                break
        if found:
            del data[uid][found]
            save_data(data)
            await m.answer(f"✅ {found} нест шуд!")
        else:
            await m.answer(f"Ёфт нашуд: '{name_to_del}'. Дар база: {list(data[uid].keys())}")
        return

    if low.startswith("баргашт "):
        parts = text.split()
        if len(parts) >= 3:
            try:
                name = " ".join(parts[1:-1])
                amount = int(parts[-1])
                # поиск имени
                found = None
                for k in data[uid].keys():
                    if k.lower() == name.lower():
                        found = k
                        break
                if found:
                    data[uid][found] = data[uid][found] - amount
                    if data[uid][found] <= 0:
                        del data[uid][found]
                    save_data(data)
                    await m.answer(f"Баргашт {amount} аз {found}")
                else:
                    await m.answer(f"Ёфт нашуд {name}")
            except:
                pass
        return

    # КАРЗ ДОДАН - Аббос 500
    parts = text.split()
    if len(parts) >= 2:
        try:
            amount = int(parts[-1])
            name = " ".join(parts[:-1])
            if name.lower() in ["нест", "баргашт"]:
                return
            # если имя уже есть с другим регистром - используем существующий
            found = None
            for k in data[uid].keys():
                if k.lower() == name.lower():
                    found = k
                    break
            if found:
                name = found
                data[uid][name] += amount
            else:
                if name not in data[uid]:
                    data[uid][name] = 0
                data[uid][name] += amount
            save_data(data)
            await m.answer(f"Карзи {amount} барои {name} сабт шуд. Бакия: {data[uid][name]}")
        except:
            pass

async def handle_web(request):
    return web.Response(text="Bot is running V3")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
