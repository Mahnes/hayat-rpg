import asyncio
import nest_asyncio
from telethon import TelegramClient
from telegram.ext import ApplicationBuilder, CommandHandler

nest_asyncio.apply()  # Event loop hatasını çözer

# TELEGRAM API BİLGİLERİ
api_id = 4054520              # buraya kendi API ID yaz
api_hash = "5b3336aceb7bf56133db69b5c837d351"        # buraya kendi API HASH yaz
bot_token = "8749138770:AAFfFQK53I2OTq5brf2TiZ5nq_n7REJBvxM"      # buraya BotFather token yaz

# GLOBAL DEĞİŞKENLER
groups = []                  # Bot üzerinden eklenecek gruplar/kanallar
message = "Merhaba"
interval = 900               # saniye cinsinden
running = False

# TELETHON CLIENT
client = TelegramClient("session", api_id, api_hash)

# MESAJ GÖNDERME DÖNGÜSÜ
async def spam_loop():
    global running
    while True:
        if running:
            for g in groups:
                try:
                    await client.send_message(g, message)
                except Exception as e:
                    print("Hata:", e)
            await asyncio.sleep(interval)
        else:
            await asyncio.sleep(5)

# TELEGRAM BOT KOMUTLARI
async def startbot(update, context):
    global running
    running = True
    await update.message.reply_text("Bot başlatıldı ✅")

async def stopbot(update, context):
    global running
    running = False
    await update.message.reply_text("Bot durduruldu ⏹")

async def setmesaj(update, context):
    global message
    message = " ".join(context.args)
    await update.message.reply_text(f"Mesaj değiştirildi:\n{message}")

async def setsure(update, context):
    global interval
    try:
        interval = int(context.args[0])
        await update.message.reply_text(f"Süre değiştirildi: {interval} saniye")
    except:
        await update.message.reply_text("Hatalı süre, sadece sayı girin!")

async def addgroup(update, context):
    group = context.args[0]
    if group not in groups:
        groups.append(group)
        await update.message.reply_text(f"Grup/Kanal eklendi:\n{group}")
    else:
        await update.message.reply_text("Bu grup zaten listede.")

async def removegroup(update, context):
    group = context.args[0]
    if group in groups:
        groups.remove(group)
        await update.message.reply_text(f"Grup/Kanal silindi:\n{group}")
    else:
        await update.message.reply_text("Bu grup listede yok.")

async def listgroups(update, context):
    if not groups:
        await update.message.reply_text("Henüz grup yok.")
    else:
        await update.message.reply_text("Gruplar:\n" + "\n".join(groups))

# ANA FONKSİYON
async def main():
    await client.start()  # Telethon userbot başlat
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("startbot", startbot))
    app.add_handler(CommandHandler("stopbot", stopbot))
    app.add_handler(CommandHandler("setmesaj", setmesaj))
    app.add_handler(CommandHandler("setsure", setsure))
    app.add_handler(CommandHandler("addgroup", addgroup))
    app.add_handler(CommandHandler("removegroup", removegroup))
    app.add_handler(CommandHandler("groups", listgroups))

    asyncio.create_task(spam_loop())
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
