from telegram.ext import *
import datetime, os, json

FILE="debts.json"
def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def save(d):
    with open(FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False)

debts=load()

async def start(u,c):
    await u.message.reply_text("Али 200 = илова\nНест Али = нест\n/qarz = руйхат")

async def qarz(u,c):
    if not debts:
        await u.message.reply_text("Холӣ")
        return
    t=""
    for k,v in debts.items():
        s=v['s'] if isinstance(v,dict) else v
        due=v.get('due') if isinstance(v,dict) else None
        if due and due>0:
            t+=f"{k}: {s}с - {due} руз монд\n"
        else:
            t+=f"{k}: {s}с\n"
    await u.message.reply_text(t)

async def txt(u,c):
    global debts
    m=u.message.text.strip()
    low=m.lower()

    if low=="ха":
        debts={}
        save(debts)
        await u.message.reply_text("Тоза шуд")
        return

    if low.startswith("нест"):
        name=low.replace("нест кун","").replace("нест","").strip()
        found=[k for k in debts.keys() if name in k.lower()]
        if not found:
            await u.message.reply_text(f"Ёфт нашуд. Хаст: {', '.join(debts.keys())}")
            return
        for k in found: del debts[k]
        save(debts)
        await u.message.reply_text(f"✅ Нест шуд: {', '.join(found)}")
        return

    try:
        parts=m.split()
        sum_idx=-1
        for i,p in enumerate(parts):
            if p.isdigit(): sum_idx=i; break
        if sum_idx==-1: raise ValueError
        name=" ".join(parts[:sum_idx]).strip()
        sum_val=int(parts[sum_idx])
        # срок
        rest=" ".join(parts[sum_idx+1:]).lower()
        due=0
        if "завтра" in rest or "пагох" in rest: due=1
        elif rest.isdigit(): due=int(rest)
        elif "7" in rest: due=7

        debts[name]={'s':sum_val,'due':due}
        save(debts)
        await u.message.reply_text(f"Сабт: {name} = {sum_val} {f'+ {due} руз' if due else ''}")
    except:
        await u.message.reply_text("Мисол: Аббос 500 ё Аббос 500 7")

def get_handlers():
    return [CommandHandler("start",start),CommandHandler("qarz",qarz),MessageHandler(filters.TEXT & ~filters.COMMAND, txt)]
