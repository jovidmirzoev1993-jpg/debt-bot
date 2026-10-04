import os, logging, requests
from collections import defaultdict
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
SHEET_URL = os.getenv("SHEET_URL")
logging.basicConfig(level=logging.INFO)

def load_data():
    try:
        if not SHEET_URL: return []
        r = requests.get(SHEET_URL, timeout=15)
        return r.json() # [{"name":"Аббос","amount":5000,"date":"..."}]
    except Exception as e:
        print(f"load error {e}")
        return []

def save_add(name, amount):
    try:
        date = datetime.now().strftime("%d.%m.%Y")
        requests.post(SHEET_URL, json={"action":"add","name":name,"amount":amount,"date":date}, timeout=15)
    except Exception as e:
        print(f"save error {e}")

def save_return(name, amount):
    try:
        date = datetime.now().strftime("%d.%m.%Y")
        requests.post(SHEET_URL, json={"action":"add","name":name,"amount":-amount,"date":date}, timeout=15)
    except: pass

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот пайваст ба Google Диск ✅\nАббос 5000 - қарз додан\nБаргашт Аббос 500 - баргашт\n/qarz - рӯйхат\n/hisob - ҳисобот")

async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text: return

    low = text.lower()
    # Баргашт
    if low.startswith("баргашт ") or low.startswith("bargasht "):
        try:
            parts = text.split()
            name = parts[1]
            amount = float(parts[2].replace(",","."))
            save_return(name, amount)
            await update.message.reply_text(f"✅ Баргашт: {name} - {amount}")
        except: await update.message.reply_text("Нависед: Баргашт Аббос 500")
        return

    # Нест
    if low.startswith("нест ") or low.startswith("nest "):
        name = text.split(" ",1)[1].strip()
        try:
            requests.post(SHEET_URL, json={"action":"delete","name":name}, timeout=15)
            await update.message.reply_text(f"✅ {name} нест карда шуд аз база")
        except: pass
        return

    # Қарз додан: Аббос 5000
    parts = text.rsplit(" ",1)
    if len(parts)!=2: return
    name, amount_str = parts
    try:
        amount = float(amount_str.replace(",","."))
    except: return

    save_add(name.strip(), amount)
    # ҳисоби нав
    data = load_data()
    total_for = sum(float(d.get('amount',0)) for d in data if d.get('name','').lower()==name.strip().lower())
    await update.message.reply_text(f"Қарзи {amount} барои {name} сабт шуд.\nБақияи нав: {total_for} сомонӣ.")

async def qarz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("Рӯйхат холӣ аст.")
        return

    sums = defaultdict(float)
    last_date = {}
    for d in data:
        n = d.get('name','').strip()
        if not n: continue
        sums[n] += float(d.get('amount',0))
        last_date[n] = d.get('date','')

    # фақат қарздорон бо бақия > 0
    active = {k:v for k,v in sums.items() if v>0.01}
    if not active:
        await update.message.reply_text("Ҳама қарзҳо баргаштанд ✅")
        return

    msg = "📒 Дафтари қарз:\n"
    i=1
    total=0
    for name, bal in active.items():
        msg+=f"{i}. {name} — {bal:g} сомонӣ — {last_date.get(name,'')}\n"
        total+=bal
        i+=1
    msg+=f"💰 Ҷамъ: {total:g} сомонӣ\n👥 {len(active)} нафар қарздор"
    await update.message.reply_text(msg)

async def hisob(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await qarz(update, ctx)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("qarz", qarz))
    app.add_handler(CommandHandler("hisob", hisob))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__=="__main__":
    main()
