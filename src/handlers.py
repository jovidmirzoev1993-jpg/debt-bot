from telegram.ext import *
import datetime, os, json

FILE="debts.json"
def load():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}
def save(d):
    with open(FILE,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False)

debts=load()

async def start(u,c):
    await u.message.reply_text("Али 200 = добавить\nНест Али = удалить\n/qarz = список\n/toza = очистить\n\nПример с сроком: Али 200 7 (на 7 дней)")

async def qarz(u,c):
    if not debts:
        await u.message.reply_text("Холӣ")
        return
    t=""
    for k,v in debts.items():
        # v может быть число или dict
        s=v['s'] if isinstance(v,dict) else v
        t+=f"{k}: {s}\n"
    await u.message.reply_text(t)

async def toza(u,c):
    await u.message.reply_text("ХА нависед барои тоза кардан")

async def txt(u,c):
    global debts
    m=u.message.text.strip()
    low=m.lower()

    # ТОЗА с подтверждением
    if low=="ха":
        debts={}
        save(debts)
        await u.message.reply_text("Тоза шуд")
        return

    # УДАЛЕНИЕ УМНОЕ - ищет по части имени!
    if low.startswith("нест"):
        name=low.replace("нест кун","").replace("нест","").strip()
        if not name:
            await u.message.reply_text("Кого? Напиши: Нест Аббос")
            return
        found=[]
        for k in list(debts.keys()):
            if name in k.lower(): # <-- главное! ищет внутри
                found.append(k)
        if not found:
            await u.message.reply_text(f"Ёфт нашуд '{name}'. Дорем: {', '.join(debts.keys())}")
            return
        for k in found:
            del debts[k]
        save(debts)
        await u.message.reply_text(f"✅ Нест шуд: {', '.join(found)}")
        return

    # ДОБАВЛЕНИЕ - правильно парсит
    try:
        # убираем слово завтра/сегодня из суммы
        parts=m.split()
        # находим число
        sum_idx=-1
        sum_val=0
        for i,p in enumerate(parts):
            if p.isdigit():
                sum_idx=i
                sum_val=int(p)
                break
        if sum_idx==-1:
            raise ValueError
        name=" ".join(parts[:sum_idx]).strip()
        # срок
        due_text=" ".join(parts[sum_idx+1:]).lower()
        due_days=0
        if "завтра" in due_text: due_days=1
        elif "пагоҳ" in due_text: due_days=1
        elif due_text.isdigit(): due_days=int(due_text)

        if not name:
            raise ValueError

        debts[name]= {'s':sum_val, 'due':due_days}
        save(debts)
        txt=f"Қарзи {sum_val} барои {name} сабт шуд. Бақия: {sum_val}"
        if due_days>0:
            txt+=f"\n⏰ Муҳлат: {due_days} рӯз (то {(datetime.date.today()+datetime.timedelta(days=due_days))})"
        await u.message.reply_text(txt)

    except:
        await u.message.reply_text("Нависед: Аббос 500 или Аббос 500 7")

def get_handlers():
    return [CommandHandler("start",start),CommandHandler("qarz",qarz),CommandHandler("toza",toza),MessageHandler(filters.TEXT & ~filters.COMMAND, txt)]
