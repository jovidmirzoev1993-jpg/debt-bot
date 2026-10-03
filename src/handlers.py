from telegram import Update
from telegram.ext import *
import datetime
debts={}
def now():
 return str(datetime.date.today())
async def r(u,t):
 await u.message.reply_text(t)
async def start(u,c):
 await r(u,"Qarz daftar\nAli 200\n/qarz")
async def qarz(u,c):
 if not debts:
  await r(u,"Holi")
  return
 s="Daftar:\n"
 j=0
 for k,v in debts.items():
  j+=1
  s+=f"{j}. {k} - {v['s']} - {v['d']}\n"
 tot=sum(x['s'] for x in debts.values())
 s+=f"Jam: {tot}\n{j} nafar"
 await r(u,s)
async def hisob(u,c):
 tot=sum(x['s'] for x in debts.values())
 await r(u,f"Jam: {tot}")
async def toza(u,c):
 debts.clear()
 await r(u,"Toza")
async def txt(u,c):
 m=u.message.text.strip()
 l=m.lower()
 if l.startswith("нест кун"):
  nm=m[8:].strip()
  await do_del(u,nm)
  return
 if l.startswith("нест"):
  nm=m[5:].strip()
  await do_del(u,nm)
  return
 try:
  a,b=m.rsplit(' ',1)
  n=int(b)
  if a in debts:
   debts[a]['s']+=n
   debts[a]['d']=now()
  else:
   debts[a]={'s':n,'d':now()}
  if debts[a]['s']<=0:
   del debts[a]
   await r(u,f"{a} toza")
  else:
   ba=debts[a]['s']
   await r(u,f"Sabt {a}\nBaqiya {ba}")
 except:
  await r(u,"Navis: Ali 200")
async def do_del(u,nm):
 for k in list(debts.keys()):
  if k.lower()==nm.lower():
   del debts[k]
   await r(u,f"{k} nest")
   return
 await r(u,"Yoft nashud")
def get_handlers():
 return[
  CommandHandler("start",start),
  CommandHandler("qarz",qarz),
  CommandHandler("hisob",hisob),
  CommandHandler("toza",toza),
  MessageHandler(filters.TEXT & ~filters.COMMAND,txt)
 ]
