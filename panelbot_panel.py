# panelbot_panel.py

import asyncio
import nest_asyncio
from telethon import TelegramClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler
import random
import os

nest_asyncio.apply()  # Event loop hatalarını önler

# --------------- TELEGRAM API BİLGİLERİ ---------------
api_id = 4054520                # my.telegram.org dan al
api_hash = "5b3336aceb7bf56133db69b5c837d351"          # my.telegram.org dan al
bot_token = "8749138770:AAFfFQK53I2OTq5brf2TiZ5nq_n7REJBvxM"        # BotFather dan al

# --------------- GLOBAL DEĞİŞKENLER ---------------
groups = []                     # Grup veya kanal listesi
messages = ["Merhaba!", "Selam!", "Bugün nasılsın?"]  # Rastgele mesaj listesi
message = messages[0]
interval = 900                  # saniye
running = False
photo_path = None               # Gönderilecek fotoğraf yolu

# --------------- TELETHON CLIENT ---------------
client = TelegramClient("session", api_id, api_hash)

# --------------- MESAJ GÖNDERME DÖNGÜSÜ ---------------
async def spam_loop():
    global running, message, groups, photo_path
    while True:
        if running and groups:
            for g in groups:
                try:
                    send_msg = random.choice(messages) if len(messages) > 1 else message
                    if photo_path and os.path.exists(photo_path):
                        await client.send_file(g, photo_path, caption=send_msg)
                    else:
                        await client.send_message(g, send_msg)
                except Exception as e:
                    print("Hata ->", g, e)
            await asyncio.sleep(interval)
        else:
            await asyncio.sleep(5)

# --------------- PANEL BUTONLARI ---------------
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Başlat", callback_data="start"),
         InlineKeyboardButton("Durdur", callback_data="stop")],
        [InlineKeyboardButton("Mesaj Değiştir", callback_data="setmsg"),
         InlineKeyboardButton("Süre Değiştir", callback_data="settime")],
        [InlineKeyboardButton("Grup Ekle", callback_data="addgroup"),
         InlineKeyboardButton("Grup Sil", callback_data="rmgroup")],
        [InlineKeyboardButton("Gruplar", callback_data="listgroups")],
        [InlineKeyboardButton("Foto Seç", callback_data="setphoto")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --------------- CALLBACK QUERY HANDLER ---------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global running, message, interval, groups, photo_path
    query = update.callback_query
    await query.answer()
    
    if query.data == "start":
        running = True
        await query.edit_message_text(text="Bot Başlatıldı ✅", reply_markup=main_keyboard())
    elif query.data == "stop":
        running = False
        await query.edit_message_text(text="Bot Durduruldu ⏹", reply_markup=main_keyboard())
    elif query.data == "setmsg":
        await query.edit_message_text(text="Yeni mesaj için /setmsg <mesaj> yazın", reply_markup=main_keyboard())
    elif query.data == "settime":
        await query.edit_message_text(text="Yeni süre için /settime <saniye> yazın", reply_markup=main_keyboard())
    elif query.data == "addgroup":
        await query.edit_message_text(text="Grup eklemek için /addgroup <@grupadi veya link> yazın", reply_markup=main_keyboard())
    elif query.data == "rmgroup":
        await query.edit_message_text(text="Grup silmek için /rmgroup <@grupadi veya link> yazın", reply_markup=main_keyboard())
    elif query.data == "listgroups":
        if not groups:
            await query.edit_message_text(text="Henüz grup yok.", reply_markup=main_keyboard())
        else:
            await query.edit_message_text(text="Gruplar:\n" + "\n".join(groups), reply_markup=main_keyboard())
    elif query.data == "setphoto":
        await query.edit_message_text(text="Fotoğraf göndermek için /setphoto <dosya yolu> yazın", reply_markup=main_keyboard())

# --------------- KOMUTLAR ---------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Panel Başlatıldı", reply_markup=main_keyboard())

async def setmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message
    text = " ".join(context.args)
    if text:
        message = text
        await update.message.reply_text(f"Mesaj değiştirildi: {message}")
    else:
        await update.message.reply_text("Hatalı kullanım! Örnek: /setmsg Merhaba")

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global interval
    try:
        t = int(context.args[0])
        interval = t
        await update.message.reply_text(f"Süre değiştirildi: {interval} saniye")
    except:
        await update.message.reply_text("Hatalı süre, sadece sayı girin! Örnek: /settime 900")

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global groups
    g = context.args[0]
    if g not in groups:
        groups.append(g)
        await update.message.reply_text(f"Grup/Kanal eklendi: {g}")
    else:
        await update.message.reply_text("Bu grup zaten listede.")

async def rmgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global groups
    g = context.args[0]
    if g in groups:
        groups.remove(g)
        await update.message.reply_text(f"Grup/Kanal silindi: {g}")
    else:
        await update.message.reply_text("Bu grup listede yok.")

async def setphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global photo_path
    p = context.args[0]
    if os.path.exists(p):
        photo_path = p
        await update.message.reply_text(f"Fotoğraf yolu ayarlandı: {photo_path}")
    else:
        await update.message.reply_text("Dosya bulunamadı!")

# --------------- ANA FONKSİYON ---------------
async def main():
    await client.start()
    app = ApplicationBuilder().token(bot_token).build()
    
    # Komutlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setmsg", setmsg))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("addgroup", addgroup))
    app.add_handler(CommandHandler("rmgroup", rmgroup))
    app.add_handler(CommandHandler("setphoto", setphoto))
    
    # Butonlar
    app.add_handler(CallbackQueryHandler(button))
    
    # Mesaj döngüsü
    asyncio.create_task(spam_loop())
    
    # Botu çalıştır
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
