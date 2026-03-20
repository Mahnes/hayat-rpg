import requests, json, random, datetime, re
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ---------------------- SETTINGS ----------------------
BOT_TOKEN = "8745064981:AAGDuGG1oX-zGYP84kGS5_GBNGzrOLPfEvY"
TRLINK_API_KEY = "262fedeb44caf0e4f4440c2293661f0e924ec1b2"
ADMINS = [5475530776]  # Telegram IDs of admins
USERS_FILE = "users.json"
DAILY_BONUS_AMOUNT = 10

# ---------------------- SAMPLE CONTENT ----------------------
random_movies = ["The Amazing Race", "Insidious", "Avatar", "The Conjuring", "John Wick"]
random_tvshows = ["Breaking Bad", "The Umbrella Academy", "The Boys", "Friends", "The Office"]

# ---------------------- HELPERS ----------------------
def load_users():
    try:
        with open(USERS_FILE, "r") as f: return json.load(f)
    except: return {}

def save_users(users):
    with open(USERS_FILE, "w") as f: json.dump(users, f, indent=2)

def shorten_link(url):
    r = requests.get(f"https://ay.live/api/?api={TRLINK_API_KEY}&url={url}&format=text")
    return r.text.strip()

def slugify(text):
    text = text.lower()
    text = text.replace("ı","i").replace("ğ","g").replace("ü","u").replace("ş","s").replace("ö","o").replace("ç","c")
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return text.strip().replace(" ","+")

# ---------------------- BOT HANDLERS ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    if user_id not in users:
        users[user_id] = {"username": update.effective_user.username,
                          "active": True,
                          "referrals": 0,
                          "last_seen": str(datetime.date.today()),
                          "bonus_claimed": False}
        save_users(users)

    keyboard = [["📺 Search TV Show", "🎬 Search Movie"], ["🎲 Random Suggestion", "ℹ️ Help"]]
    await update.message.reply_text(
        f"🎬 Welcome {update.effective_user.first_name}! What would you like to watch?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    users = load_users()

    # ---------------------- ADMIN COMMANDS ----------------------
    if user_id in map(str, ADMINS):
        if text.startswith("/admin"):
            await update.message.reply_text(
                "✅ Admin Panel\n"
                "/stats - View user statistics\n"
                "/users - List all users\n"
                "/broadcast <message> - Send message to all users\n"
                "/ban <user_id> - Ban a user\n"
                "/unban <user_id> - Unban a user\n"
                "/bonus <user_id> <amount> - Give bonus"
            )
            return
        if text.startswith("/stats"):
            total = len(users)
            active = sum(1 for u in users.values() if u.get("active"))
            await update.message.reply_text(f"📊 Total users: {total}\n✅ Active users: {active}")
            return
        if text.startswith("/users"):
            msg = ""
            for uid, u in users.items():
                msg += f"{uid} - {u.get('username')} - {'Active' if u.get('active') else 'Banned'}\n"
            await update.message.reply_text(msg if msg else "No users found.")
            return
        if text.startswith("/broadcast"):
            msg = " ".join(text.split()[1:])
            for uid in users:
                try: await context.bot.send_message(chat_id=int(uid), text=msg)
                except: continue
            await update.message.reply_text("✅ Message sent to all users!")
            return
        if text.startswith("/ban"):
            uid = text.split()[1]
            if uid in users: users[uid]["active"] = False; save_users(users)
            await update.message.reply_text(f"❌ User {uid} has been banned")
            return
        if text.startswith("/unban"):
            uid = text.split()[1]
            if uid in users: users[uid]["active"] = True; save_users(users)
            await update.message.reply_text(f"✅ User {uid} has been unbanned")
            return
        if text.startswith("/bonus"):
            parts = text.split()
            uid, amt = parts[1], int(parts[2])
            if uid in users:
                users[uid]["bonus_claimed"] = True
                save_users(users)
            await update.message.reply_text(f"💰 {amt} bonus given to user {uid}")
            return

    # ---------------------- USER INTERACTIONS ----------------------
    if text == "📺 Search TV Show":
        context.user_data["type"] = "tvshow"
        await update.message.reply_text("📺 Type the name of the TV Show:")
        return
    elif text == "🎬 Search Movie":
        context.user_data["type"] = "movie"
        await update.message.reply_text("🎬 Type the name of the Movie:")
        return
    elif text == "🎲 Random Suggestion":
        choice_type = random.choice(["tvshow", "movie"])
        choice_item = random.choice(random_tvshows if choice_type=="tvshow" else random_movies)
        query = slugify(choice_item)
        link = f"https://myflixerz.to/search/{query}"
        short = shorten_link(link)
        await update.message.reply_text(f"🎲 Random Suggestion ({choice_type.upper()})\n🎬 {choice_item}\n📺 Click the link below to watch 👇\n{short}")
        return
    elif text == "ℹ️ Help":
        await update.message.reply_text("1️⃣ Select TV Show or Movie\n2️⃣ Type its name\n3️⃣ Bot will give you a TRLink to watch it 🎥\n🎲 You can also get a random suggestion!")
        return

    # ---------------------- SEARCH FUNCTION ----------------------
    content_type = context.user_data.get("type")
    if not content_type:
        await update.message.reply_text("Please select TV Show or Movie first!")
        return

    query = slugify(text)
    link = f"https://myflixerz.to/search/{query}"
    short = shorten_link(link)
    await update.message.reply_text(f"🎬 {text}\n📺 Click the link below to watch 👇\n{short}")

# ---------------------- RUN BOT ----------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.run_polling()
