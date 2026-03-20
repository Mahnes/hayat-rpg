import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import LeaveChannelRequest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- AYARLAR ---
api_id = 4054520
api_hash = "5b3336aceb7bf56133db69b5c837d351"
bot_token = "8620314868:AAE8909RBke4t-Z7djbbawWFukNRApm0FRo"

client = TelegramClient("session", api_id, api_hash)

# --- GLOBAL DEĞİŞKENLER ---
dialogs_cache = []
selected_groups = set() # Seçilen indeksleri tutar
bulk_mode = False

async def load_groups():
    global dialogs_cache
    print("Gruplar taranıyor...")
    dialogs_cache = []
    # Sadece kanal ve grupları çekiyoruz
    async for d in client.iter_dialogs():
        if d.is_group or d.is_channel:
            dialogs_cache.append(d)
    print(f"{len(dialogs_cache)} adet grup/kanal bulundu.")

def build_keyboard():
    keyboard = []
    
    # Grupları listele (Çok fazla grup varsa ilk 50 tanesini gösterir - Telegram limitidir)
    for i, g in enumerate(dialogs_cache[:50]):
        name = g.name
        # Eğer bu grup seçiliyse başına check koy
        if bulk_mode and i in selected_groups:
            name = "✅ " + name
        
        keyboard.append([InlineKeyboardButton(name, callback_data=f"group_{i}")])

    # Alt kontrol butonları
    control_buttons = []
    if not bulk_mode:
        control_buttons.append(InlineKeyboardButton("📦 Toplu Seçim Modu", callback_data="bulk_on"))
    else:
        control_buttons.append(InlineKeyboardButton("🚪 Seçilenlerden Çık", callback_data="bulk_leave"))
        control_buttons.append(InlineKeyboardButton("❌ İptal", callback_data="bulk_off"))
    
    keyboard.append(control_buttons)
    keyboard.append([InlineKeyboardButton("🔄 Listeyi Yenile", callback_data="refresh")])
    
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await load_groups()
    await update.message.reply_text("Yönetmek istediğin grup/kanalları seç:", reply_markup=build_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bulk_mode, selected_groups
    query = update.callback_query
    data = query.data
    await query.answer()

    # 1. Grup Seçimi
    if data.startswith("group_"):
        index = int(data.split("_")[1])
        
        if bulk_mode:
            if index in selected_groups:
                selected_groups.remove(index)
            else:
                selected_groups.add(index)
            await query.edit_message_reply_markup(reply_markup=build_keyboard())
        else:
            # Tekli modda onay sor
            group = dialogs_cache[index]
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Evet, Çık", callback_data=f"leave_{index}")],
                [InlineKeyboardButton("Vazgeç", callback_data="refresh")]
            ])
            await query.edit_message_text(f"⚠️ {group.name} grubundan çıkmak istediğine emin misin?", reply_markup=keyboard)

    # 2. Toplu Modu Aç/Kapat
    elif data == "bulk_on":
        bulk_mode = True
        selected_groups.clear()
        await query.edit_message_reply_markup(reply_markup=build_keyboard())

    elif data == "bulk_off":
        bulk_mode = False
        selected_groups.clear()
        await query.edit_message_reply_markup(reply_markup=build_keyboard())

    # 3. Toplu Çıkış İşlemi
    elif data == "bulk_leave":
        if not selected_groups:
            return
        
        await query.edit_message_text("İşlem başlatıldı, lütfen bekleyin...")
        
        count = 0
        for i in list(selected_groups):
            try:
                group = dialogs_cache[i]
                await client(LeaveChannelRequest(group.entity))
                count += 1
                await asyncio.sleep(0.5) # Telegram engeline takılmamak için
            except Exception as e:
                print(f"Hata: {e}")
        
        selected_groups.clear()
        bulk_mode = False
        await load_groups()
        await query.edit_message_text(f"✅ Başarıyla {count} gruptan çıkıldı.")
        await asyncio.sleep(2)
        await query.edit_message_text("Güncel liste:", reply_markup=build_keyboard())

    # 4. Tekli Çıkış İşlemi
    elif data.startswith("leave_"):
        index = int(data.split("_")[1])
        try:
            await client(LeaveChannelRequest(dialogs_cache[index].entity))
            await query.edit_message_text("Gruptan çıkıldı.")
        except:
            await query.edit_message_text("Hata oluştu.")
        
        await asyncio.sleep(1)
        await load_groups()
        await query.edit_message_text("Grup / Kanal seç:", reply_markup=build_keyboard())

    # 5. Listeyi Yenile
    elif data == "refresh":
        await load_groups()
        await query.edit_message_text("Liste güncellendi:", reply_markup=build_keyboard())

async def main():
    # Telethon başlat
    await client.start()
    
    # PTB (Bot arayüzü) başlat
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot hazır ve çalışıyor...")
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        # Botun kapanmaması için sonsuz döngü
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        # Yeni yöntem: asyncio.run() otomatik olarak loop oluşturur ve kapatır.
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot kapatılıyor...")
    except Exception as e:
        print(f"Beklenmedik bir hata: {e}")

