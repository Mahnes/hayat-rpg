import json
import random
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8735720097:AAFpD-okpE6vHOlHxr1lAO5jlQqSZLwp5j0"

DATA_FILE = "data.json"

baliklar = [
"İstavrit","Gümüş","İzmarit","Ispari","Karagöz","Sargoz","Sardalya","Kupes","Mercan",
"Mezgit","Barbun","Çipura","Levrek","Palamut","Lüfer","Kalkan",
"Orkinos","Akya","Lagos","Orfoz","Kılıç Balığı","Mavi Yüzgeçli Orkinos","Marlin"
]

oltalar = {
"Eski Gölet Kamışı": ["İstavrit","Gümüş"],
"Esnek Bambu": ["İstavrit","Gümüş","İzmarit","Ispari","Karagöz","Sargoz","Sardalya","Kupes","Mercan"],
"Titanyum Alaşım": ["Kupes","Mercan","Mezgit","Barbun","Çipura","Levrek","Palamut","Lüfer","Kalkan"],
"Kusursuz Karbon S": ["Lüfer","Kalkan","Orkinos","Akya","Lagos","Orfoz","Kılıç Balığı","Mavi Yüzgeçli Orkinos","Marlin"]
}

olta_fiyat = {
"Esnek Bambu":150,
"Titanyum Alaşım":400,
"Kusursuz Karbon S":900
}

def load():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(DATA_FILE,"w") as f:
        json.dump(data,f)

data = load()

def fiyat(balik):
    i = baliklar.index(balik)
    return (i+1)*7

def menu():
    return ReplyKeyboardMarkup(
        [["🎣 Balık Tut"],["🛒 Pazar"],["🎒 Envanter"]],
        resize_keyboard=True
    )

def geri():
    return ReplyKeyboardMarkup([["⬅️ Geri"]], resize_keyboard=True)

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):

    user = str(update.effective_user.id)

    if user not in data:
        data[user]={
        "para":0,
        "olta":"Eski Gölet Kamışı",
        "envanter":{}
        }
        save(data)

        await update.message.reply_text(
        "Hoş geldin!\n\nİlk balığını tutmak için sana bir olta verdim.\n\n🎣 Eski Gölet Kamışı",
        reply_markup=menu()
        )
    else:
        await update.message.reply_text("Tekrar hoş geldin!", reply_markup=menu())

async def mesaj(update:Update, context:ContextTypes.DEFAULT_TYPE):

    user = str(update.effective_user.id)
    text = update.message.text
    u = data[user]

    if text=="🎣 Balık Tut":

        olta = u["olta"]
        secenek = oltalar[olta]
        balik = random.choice(secenek)

        u["envanter"][balik] = u["envanter"].get(balik,0) + 1
        save(data)

        await update.message.reply_text(
        f"🎣 Tebrikler!\n\nBir {balik} tuttun!",
        reply_markup=menu()
        )

    elif text=="🎒 Envanter":

        msg=f"💰 Altın: {u['para']}\n🎣 Olta: {u['olta']}\n\n🐟 Balıklar:\n"

        if not u["envanter"]:
            msg+="Yok"

        for b,a in u["envanter"].items():
            msg+=f"{b} x{a}\n"

        await update.message.reply_text(msg,reply_markup=menu())

    elif text=="🛒 Pazar":

        kb=ReplyKeyboardMarkup(
        [["🛍 Al","💰 Sat"],["⬅️ Geri"]],
        resize_keyboard=True
        )

        await update.message.reply_text("Pazar:",reply_markup=kb)

    elif text=="🛍 Al":

        kb = ReplyKeyboardMarkup(
        [
        ["Esnek Bambu"],
        ["Titanyum Alaşım"],
        ["Kusursuz Karbon S"],
        ["⬅️ Geri"]
        ],
        resize_keyboard=True
        )

        msg="Satılık Oltalar:\n\n"
        for o,f in olta_fiyat.items():
            msg+=f"{o} - {f} altın\n"

        await update.message.reply_text(msg,reply_markup=kb)

    elif text in olta_fiyat:

        fiyat_ = olta_fiyat[text]

        if u["para"] < fiyat_:
            await update.message.reply_text("Yeterli altının yok.",reply_markup=menu())
            return

        u["para"] -= fiyat_
        u["olta"] = text
        save(data)

        await update.message.reply_text(
        f"🎉 Yeni oltan: {text}",
        reply_markup=menu()
        )

    elif text=="💰 Sat":

        toplam=0

        for b,a in u["envanter"].items():
            toplam+=fiyat(b)*a

        if toplam==0:
            await update.message.reply_text("Satacak balığın yok.",reply_markup=geri())
            return

        u["para"]+=toplam
        u["envanter"]={}
        save(data)

        await update.message.reply_text(
        f"Tüm balıkları sattın.\nKazanç: {toplam} altın",
        reply_markup=menu()
        )

    elif text=="⬅️ Geri":

        await update.message.reply_text("Ana menü",reply_markup=menu())


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT,mesaj))

print("Bot çalışıyor...")
app.run_polling()

