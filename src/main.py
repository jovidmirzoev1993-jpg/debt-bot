import os, json, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data/debts.json"
os.makedirs("data", exist_ok=True)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("ВЕРСИЯ 3.1 ИСПРАВЛЕНО ✅\n\n+ Карз додан\n✅ Баргашт кард\n📒 Рӯйхати қарзҳо (/qarz)\n💰 Хисоби умумӣ (/hisob)\n\nНамуна: Аббос 500 / Нест Аббос")

@dp.message(Command("qarz", "hisob"))
async def show(m: types.Message):
    data = load()
    if not data:
        await m.answer("📭 Ҳоло қарз нест. База холӣ.")
        return
    if m.text.startswith("/qarz"):
        txt = "📒 Рӯйхати қарзҳо:\n"
        for name, summ in data.items():
            txt += f"• {name}: {summ} сомонӣ\n"
        await m.answer(txt)
    else:
        total = sum(data.values())
        txt = f"💰 Хисоби умумӣ:\nҶамъ: {total} сомонӣ\n👥 {len(data)} нафар қарздор"
        await m.answer(txt)

@dp.message()
async def all_handler(m: types.Message):
    text = m.text.strip()
    data = load()

    # Кнопки
    if "Хисоби умумӣ" in text or text == "/hisob":
        if not data:
            await m.answer("📭 Ҳоло қарз нест. База холӣ.\n💰 Ҷамъ: 0")
            return
        total = sum(data.values())
        await m.answer(f"💰 Хисоби умумӣ:\nҶамъ: {total} сомонӣ\n👥 {len(data)} нафар қарздор")
        return
    if "Рӯйхати қарзҳо" in text or text == "/qarz":
        if not data:
            await m.answer("📭 Рӯйхат холӣ аст.")
            return
        txt = "📒 Рӯйхати қарзҳо:\n"
        for name, summ in data.items():
            txt += f"• {name}: {summ}\n"
        await m.answer(txt)
        return
    if "Қарз додан" in text:
        await m.answer("Ном ва маблағро нависед: Масалан: Аббос 500")
        return
    if "Баргашт кард" in text:
        await m.answer("Кӣ баргашт кард? Нависед: Нест Аббос")
        return

    # Нест
    if text.lower().startswith("нест "):
        name = text[5:].strip()
        # поиск без учета регистра
        found = None
        for k in data.keys():
            if k.lower() == name.lower():
                found = k
                break
        if found:
            del data[found]
            save(data)
            await m.answer(f"✅ {found} нест шуд!")
        else:
            await m.answer(f"Ёфт нашуд: '{name}'. Дар база: {list(data.keys())}")
        return
