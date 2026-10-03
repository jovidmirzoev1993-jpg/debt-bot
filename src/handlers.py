import sqlite3, os
from decimal import Decimal
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, CallbackQueryHandler, filters, ContextTypes

BASE_DIR = os.path.dirname(__file__)
DATABASE_PATH = os.path.join(BASE_DIR, "debt.db")
user_state = {}

def fmt(a: Decimal) -> str:
    return f"{a:.0f}" if a == int(a) else f"{a:.2f}"

def init_db():
    with sqlite3.connect(DATABASE_PATH, timeout=10) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS debt_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, debtor_name TEXT, amount TEXT, created_at TEXT, due_date TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY, remind_enabled INTEGER DEFAULT 0)""")
        c.commit()
init_db()

def main_kb():
    return ReplyKeyboardMarkup([
        ["📒 Рӯйхати қарзҳо", "📊 Ҳисоби умумӣ"],
        ["➕ Қарз додан", "💸 Баргашт кард"],
        ["🗑️ Тоза кардан", "⏰ Напоминание"]
    ], resize_keyboard=True)

def get_debtors(uid):
    with sqlite3.connect(DATABASE_PATH, timeout=10) as c:
        rows = c.execute("SELECT debtor_name, amount FROM debt_entries WHERE user_id=?", (uid,)).fetchall()
    totals={}
    for n,a in rows:
        k=n.casefold()
        if k not in totals: totals[k]=[n, Decimal("0")]
        totals[k][1]+=Decimal(a)
    return [(n,t) for n,t in totals.values() if t>0]

def debt_book_lines(uid):
    with sqlite3.connect(DATABASE_PATH, timeout=10) as c:
        rows = c.execute("SELECT debtor_name, amount, created_at, due_date FROM debt_entries WHERE user_id=? ORDER BY id DESC",(uid,)).fetchall()
    totals,last,due_m={}, {}, {}
    for name,amt,created,due in rows:
        k=name.casefold()
        if k not in totals:
            totals[k]=[name,Decimal("0")]; last[k]=created or ""; due_m[k]=due or ""
        totals[k][1]+=Decimal(amt)
        if created and created>last.get(k,""): last[k]=created; due_m[k]=due or ""
    balances=sorted([(n,t) for n,t in totals.values() if t>0], key=lambda x: x[1], reverse=True)
    total_sum=sum((a for _,a in balances), Decimal("0"))
    lines=["📒 Дафтари қарз:"]
    if balances:
        for i,(n,a) in enumerate(balances,1):
            d=(last.get(n.casefold(),"")[:10] or ""); due=due_m.get(n.casefold(),"")
            lines.append(f"{i}. {n} — {fmt(a)} сомонӣ — {d}{' ⏰ то '+due if due else ''}")
    else: lines.append("Ҳоло қарз нест.")
    lines.extend(["",f"💰 Ҷамъ: {fmt(total_sum)}", f"👥 {len(balances)} нафар"])
    return lines

def get_overdue(uid):
    with sqlite3.connect(DATABASE_PATH, timeout=10) as c:
        rows=c.execute("SELECT debtor_name, amount, due_date FROM debt_entries WHERE user_id=?",(uid,)).fetchall()
    totals,due_m={}, {}
    for n,a,d in rows:
        k=n.casefold()
        if k not in totals: totals[k]=[n,Decimal("0")]
        totals[k][1]+=Decimal(a)
        if d: due_m[k]=d
    today=datetime.now().date().isoformat()
    return [(totals[k][0],totals[k][1],due_m[k]) for k in totals if totals[k][1]>0 and k in due_m and due_m[k]<today]

async def handle_callback_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = update.effective_user.id
    d = q.data
    if d.startswith("ret:"):
        name=d[4:]; user_state[uid]={'action':'return','name':name}
        await q.edit_message_text(f"💸 {name} чанд баргардонд? Нависед: 200")
    elif d.startswith("del:"):
        name=d[4:]
        kb=InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ Ҳа, {name}", callback_data=f"del_confirm:{name}"), InlineKeyboardButton("❌ Не", callback_data="del_cancel")]])
        await q.edit_message_text(f"🗑️ {name}-ро тоза кунем?", reply_markup=kb)
    elif d.startswith("del_confirm:"):
        name=d[12:]
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            conn.execute("DELETE FROM debt_entries WHERE user_id=? AND debtor_name=?",(uid,name)); conn.commit()
        user_state.pop(uid,None)
        await q.edit_message_text(f"✅ {name} тоза шуд.")
        await context.bot.send_message(uid, "Меню:", reply_markup=main_kb())
    elif d=="del_cancel":
        await q.edit_message_text("Бекор шуд.")
    elif d in ["rem_on","rem_off"]:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            conn.execute("INSERT INTO user_settings(user_id,remind_enabled) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET remind_enabled=?",(uid,1 if d=="rem_on" else 0,1 if d=="rem_on" else 0)); conn.commit()
        await q.edit_message_text("✅ Фаъол" if d=="rem_on" else "❌ Хомӯш")
    elif d=="rem_check":
        over=get_overdue(uid)
        if over:
            txt="\n".join([f"⏰ Мӯҳлати гузашта:"]+[f"• {n} {fmt(t)} то {du}" for n,t,du in over])
            await q.edit_message_text(txt)
        else:
            await q.edit_message_text("✅ Мӯҳлати гузашта нест.")

async def handle_message_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = (update.message.text or "").strip()
    st = user_state.get(uid)
    if text == "/start":
        await update.message.reply_text("Салом! v2 🚀\n➕ Қарз додан\n💸 Баргашт кард\n🗑️ Тоза кардан\n⏰ Напоминание\nНамуна: Али 1000 то 2026-10-20", reply_markup=main_kb())
        return
    if text == "📒 Рӯйхати қарзҳо":
        await update.message.reply_text("\n".join(debt_book_lines(uid)), reply_markup=main_kb()); return
    if text == "📊 Ҳисоби умумӣ":
        lines=debt_book_lines(uid); await update.message.reply_text("\n".join(lines[-2:]), reply_markup=main_kb()); return
    if text == "➕ Қарз додан":
        user_state[uid]={'action':'add'}; await update.message.reply_text("Номро нависед: Али"); return
    if text == "💸 Баргашт кард":
        debtors=get_debtors(uid)
        if not debtors: await update.message.reply_text("Қарздор нест", reply_markup=main_kb()); return
        kb=InlineKeyboardMarkup([[InlineKeyboardButton(f"{n} ({fmt(t)})", callback_data=f"ret:{n}")] for n,t in debtors[:20]])
        await update.message.reply_text("Кӣ баргардонд?", reply_markup=kb); return
    if text == "🗑️ Тоза кардан":
        debtors=get_debtors(uid)
        if not debtors: await update.message.reply_text("Қарздор нест", reply_markup=main_kb()); return
        kb=InlineKeyboardMarkup([[InlineKeyboardButton(f"🗑️ {n}", callback_data=f"del:{n}")] for n,t in debtors[:20]])
        await update.message.reply_text("Кӣро тоза кунем?", reply_markup=kb); return
    if text == "⏰ Напоминание":
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Фаъол", callback_data="rem_on"), InlineKeyboardButton("❌ Хомӯш", callback_data="rem_off")],[InlineKeyboardButton("🔍 Санҷиш ҳозир", callback_data="rem_check")]])
        await update.message.reply_text("⏰ Напоминание:", reply_markup=kb); return
    if st and st['action']=='add' and 'name' not in st:
        if " " not in text:
            user_state[uid]={'action':'add','name':text}
            await update.message.reply_text(f"Барои {text} чанд? 1000"); return
    if st and st['action']=='add' and 'name' in st:
        name=st['name']; due=""
        if " то " in text: text,due=text.split(" то ",1); due=due.strip()[:10]
        try:
            amt=Decimal(text.replace(",","."))
            with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
                conn.execute("INSERT INTO debt_entries (user_id,debtor_name,amount,created_at,due_date) VALUES (?,?,?,?,?)",(uid,name,str(amt),datetime.now().isoformat(),due)); conn.commit()
            user_state.pop(uid,None)
            await update.message.reply_text(f"✅ {name} {fmt(amt)} сабт шуд", reply_markup=main_kb())
        except: await update.message.reply_text("Рақам: 1000")
        return
    if st and st['action']=='return':
        name=st['name']
        try:
            amt=Decimal(text.replace(",","."))
            with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
                conn.execute("INSERT INTO debt_entries (user_id,debtor_name,amount,created_at,due_date) VALUES (?,?,?,?,?)",(uid,name,str(-abs(amt)),datetime.now().isoformat(),"")); conn.commit()
            user_state.pop(uid,None)
            await update.message.reply_text(f"✅ {name} {fmt(amt)} баргардонд!", reply_markup=main_kb())
        except: await update.message.reply_text("Рақам: 200")
        return
    try:
        due=""
        if " то " in text: text,due=text.split(" то ",1); due=due.strip()[:10]
        parts=text.rsplit(maxsplit=1)
        if len(parts)<2:
            await update.message.reply_text("Намуна: Али 1000", reply_markup=main_kb()); return
        name,amt_s=parts[0],parts[1]
        amt=Decimal(amt_s.replace(",","."))
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            conn.execute("INSERT INTO debt_entries (user_id,debtor_name,amount,created_at,due_date) VALUES (?,?,?,?,?)",(uid,name.strip(),str(amt),datetime.now().isoformat(),due)); conn.commit()
        await update.message.reply_text(f"✅ {name} {fmt(amt)}", reply_markup=main_kb())
    except:
        await update.message.reply_text(f"Намуна: Али 1000 ё Али 1000 то 2026-10-15", reply_markup=main_kb())

handle_message = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_func)
handle_callback = CallbackQueryHandler(handle_callback_func)
