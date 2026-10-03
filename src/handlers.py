from telegram.ext import *
import datetime, json, os

FILE="debts.json"
CHATS_FILE="chats.json"

def load(f):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as fp:
                return json.load(fp)
        except: return {} if f==FILE else []
    return {} if f==FILE else []

def save(f,data):
    with open(f,"w",encoding="utf-8") as fp:
        json.dump(data,fp,ensure_ascii=False,default=str)

debts={}
# конверт string dates to date
_raw=load(FILE)
for k,v in _raw.items():
    if 'due' in v and v['due']:
        try: v['due']=datetime.date.fromisoformat(v['due'])
        except: pass
    debts[k]=v

chats=set(load(CHATS_FILE))

def parse_due(s):
    now=datetime.date.today()
    s=s.strip()
    if s.isdigit():
        return now+datetime.timedelta(days=int(s))
    try:
        p=s.split('.')
        if len(p)==2:
            d,m=map(int,p)
            return datetime.date(now.year,m,d)
        if len(p)==3:
            d,m,y=map(int,p)
            return datetime.date(y,m,d)
    except: pass
    return None

async def start(u,c):
    chats.add(u.effective_chat.id)
    save(CHATS_FILE,list(chats))
    await u.message.reply_text("Салом! 👋\nАли 200 7 - 7 рӯз\nАли 200 15.10 - то 15.10\n/qarz\n/ogohi\nБот ҳар рӯз соати 9:00 худаш огоҳ мекунад!")

async def qarz(u,c):
    chats.add(u.effective_chat.id)
    save(CHATS_FILE,list(chats))
    if not debts:
        await u.message.reply_text("Холӣ")
        return
    now=datetime.date.today()
    t="📒 Рӯйхат:\n"
    for k,v in debts.items():
        due=v.get('due')
        if not due:
            t+=f"⚪ {k}: {v['s']}с - бе муҳлат\n"
        else:
            d=(due-now).days
            if d<0: t+=f"🔴 {k}: {v['s']}с - ГУЗАШТ {-d} рӯз!\n"
            elif d<=2: t+=f"🟡 {k}: {v['s']}с - {d} рӯз монд!\n"
            else: t+=f"🟢 {k}: {v['s']}с - {d} рӯз\n"
    await u.message.reply_text(t)

async def ogohi(u,c):
    now=datetime.date.today()
    out=[f"🔴 {k}: {v['s']}с - {(now-v['due']).days} рӯз гузашт!" for k,v in debts.items() if v.get('due') and v['due']<now]
    await u.message.reply_text("\n".join(out) if out else "✅ Просроч нест!")

async def txt_h(u,c):
    chats.add(u.effective_chat.id)
    save(CHATS_FILE,list(chats))
    m=u.message.text.strip()
    if m.lower().startswith("нест"):
        name=m[4:].strip()
        if name.lower().startswith("кун"): name=name[3:].strip()
        for k in list(debts.keys()):
            if k.lower()==name.lower():
                del debts[k]
                save(FILE,{kk:{**vv,'due':str(vv['due']) if vv.get('due') else None} for kk,vv in debts.items()})
                await u.message.reply_text(f"✅ {k} нест шуд")
                return
        await u.message.reply_text("Ёфт нашуд")
        return
    try:
        parts=m.rsplit(' ',2)
        if len(parts)==3:
            nom,summa,due_s=parts
            due=parse_due(due_s)
            if not due: raise ValueError
            debts[nom.strip()]={'s':int(summa),'due':due}
        else:
            nom,summa=m.rsplit(' ',1)
            debts[nom.strip()]={'s':int(summa),'due':None}
        save(FILE,{kk:{**vv,'due':str(vv['due']) if vv.get('due') else None} for kk,vv in debts.items()})
        await u.message.reply_text(f"✅ Сабт шуд: {m}")
    except:
        await u.message.reply_text("Мисол: Аббос 500 3 ё Аббос 500 15.10")

# Ин функсия ҳар рӯз худаш кор мекунад!
async def daily_check(context):
    now=datetime.date.today()
    msgs=[]
    for k,v in debts.items():
        due=v.get('due')
        if not due: continue
        d=(due-now).days
        if d==1: msgs.append(f"⏰ Фардо муҳлати {k} ({v['s']}с) тамом мешавад!")
        elif d==0: msgs.append(f"⚠️ Имрӯз муҳлати {k} ({v['s']}с) тамом мешавад!")
        elif d<0: msgs.append(f"🔴 {k} ({v['s']}с) - {-d} рӯз просроч! То {due}")
    if msgs and chats:
        text="🔔 Ёдрасӣ автоматӣ:\n\n"+"\n".join(msgs)
        for cid in list(chats):
            try: await context.bot.send_message(chat_id=cid,text=text)
            except: pass

def get_handlers():
    return [CommandHandler("start",start),CommandHandler("qarz",qarz),CommandHandler("ogohi",ogohi),MessageHandler(filters.TEXT & ~filters.COMMAND, txt_h)]
