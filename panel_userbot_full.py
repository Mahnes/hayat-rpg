# panel_userbot_full.py
import asyncio
import nest_asyncio
import os
import json
from telethon import TelegramClient
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from telethon.errors import FloodWaitError

nest_asyncio.apply()

# ---------- TELEGRAM API ----------
api_id = 4054520
api_hash = "5b3336aceb7bf56133db69b5c837d351"
bot_token = "8749138770:AAFfFQK53I2OTq5brf2TiZ5nq_n7REJBvxM"

# ---------- GLOBAL ----------
client = TelegramClient("session", api_id, api_hash)

groups = []
message = "Merhaba, burası varsayılan mesajdır."
interval = 900
running = False
photo_path = None
awaiting_message = {}

DATA_FILE = "data.json"

# ---------- VERİ KAYIT ----------
def save_data():
    data = {
        "message": message,
        "photo_path": photo_path,
        "groups": groups
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    global message, photo_path, groups
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            message = data.get("message", message)
            photo_path = data.get("photo_path", photo_path)
            groups = data.get("groups", groups)

# ---------- REPLY KEYBOARD ----------
def main_keyboard():

    keyboard = [
        ["Başlat", "Durdur"],
        ["Mesaj Değiştir", "Süre Değiştir"],
        ["Grup Ekle", "Grup Sil"],
        ["Grupları Göster"],
        ["Foto Seç", "Foto Kaldır"],
        ["Mesajı Göster", "Fotoğrafı Göster"]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------- SPAM LOOP ----------
async def spam_loop():
    global running

    while True:

        if running and groups:

            for g in groups:

                try:

                    if photo_path and os.path.exists(photo_path):
                        await client.send_file(g, photo_path, caption=message)
                    else:
                        await client.send_message(g, message)

                except FloodWaitError as e:
                    print("Flood wait:", e.seconds)
                    await asyncio.sleep(e.seconds)

                except Exception as e:
                    print("Hata ->", g, e)

            await asyncio.sleep(interval)

        else:
            await asyncio.sleep(5)

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Panel Başlatıldı", reply_markup=main_keyboard())

# ---------- MESAJ AYAR ----------
async def panel_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global message, running, photo_path

    text = update.message.text
    user_id = update.effective_user.id

    if awaiting_message.get(user_id):

        message = text
        awaiting_message[user_id] = False
        save_data()

        await update.message.reply_text("Mesaj kaydedildi ✅", reply_markup=main_keyboard())
        return

    # --------- BUTONLAR ---------

    if text == "Başlat":

        running = True
        await update.message.reply_text("Bot Başlatıldı ✅", reply_markup=main_keyboard())

    elif text == "Durdur":

        running = False
        await update.message.reply_text("Bot Durduruldu ⏹", reply_markup=main_keyboard())

    elif text == "Mesaj Değiştir":

        awaiting_message[user_id] = True
        await update.message.reply_text("Yeni mesajı gönder.", reply_markup=main_keyboard())

    elif text == "Süre Değiştir":

        await update.message.reply_text("Yeni süre için /settime <saniye> yazın")

    elif text == "Grup Ekle":

        await update.message.reply_text("Grup eklemek için /addgroup <@grupadi veya link> yazın")

    elif text == "Grup Sil":

        await update.message.reply_text("Grup silmek için /rmgroup <@grupadi veya link> yazın")

    elif text == "Grupları Göster":

        if not groups:
            await update.message.reply_text("Grup yok", reply_markup=main_keyboard())
        else:
            await update.message.reply_text("\n".join(groups), reply_markup=main_keyboard())

    elif text == "Foto Seç":

        await update.message.reply_text("Foto gönderin, kaydedilecek.")

    elif text == "Foto Kaldır":

        photo_path = None
        save_data()
        await update.message.reply_text("Fotoğraf kaldırıldı", reply_markup=main_keyboard())

    elif text == "Mesajı Göster":

        await update.message.reply_text(message, reply_markup=main_keyboard())

    elif text == "Fotoğrafı Göster":

        if photo_path and os.path.exists(photo_path):
            await update.message.reply_photo(photo=open(photo_path, "rb"), caption="Aktif foto")
        else:
            await update.message.reply_text("Foto yok")

# ---------- FOTOĞRAF ----------
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global photo_path

    if update.message.photo:

        file = await update.message.photo[-1].get_file()

        path = f"{os.getcwd()}/photo.jpg"

        await file.download_to_drive(path)

        photo_path = path

        save_data()

        await update.message.reply_text("Foto kaydedildi ✅", reply_markup=main_keyboard())

# ---------- KOMUTLAR ----------
async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global interval

    try:

        interval = int(context.args[0])

        await update.message.reply_text(f"Süre değişti: {interval} saniye")

    except:

        await update.message.reply_text("Hatalı süre")

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global groups

    g = context.args[0]

    if g not in groups:

        groups.append(g)

        save_data()

        await update.message.reply_text("Grup eklendi")

async def rmgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global groups

    g = context.args[0]

    if g in groups:

        groups.remove(g)

        save_data()

        await update.message.reply_text("Grup silindi")

# ---------- MAIN ----------
async def main():

    load_data()

    await client.start()

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("addgroup", addgroup))
    app.add_handler(CommandHandler("rmgroup", rmgroup))

    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, panel_message_handler))

    asyncio.create_task(spam_loop())

    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
