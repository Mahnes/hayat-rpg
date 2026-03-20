import logging, json, os, time, requests, urllib.parse
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIG ---
TOKEN = "8750080265:AAEErBmM-lXaHO0zP7FZQzK4pMuuR-CJbOo"
ADMIN_ID = 5475530776
API_KEY = "262fedeb44caf0e4f4440c2293661f0e924ec1b2"

# --- DATA MANAGEMENT ---
def load_data(file, default):
    if not os.path.exists(file):
        with open(file,'w') as f: json.dump(default,f)
    with open(file,'r') as f: return json.load(f)

def save_data(file, data):
    with open(file,'w') as f: json.dump(data,f,indent=4)

# --- LINK LOGIC ---
def generate_code(n):
    chars = "abcdefghijklmnopqrstuvwxyz"
    code = ""
    temp_n = n
    for _ in range(5):
        code = chars[temp_n % 26] + code
        temp_n //= 26
    return code

def shorten_link(long_url):
    url_encoded = urllib.parse.quote(long_url)
    api_url = f"https://ay.live/api/?api={API_KEY}&url={url_encoded}&format=text"
    try:
        r = requests.get(api_url,timeout=10)
        if r.status_code==200:
            short_link = r.text.strip()
            if short_link.startswith("http"): return short_link
            else: return "⚠️ Link generation failed. Check API key or URL."
        else: return f"⚠️ Error {r.status_code} from API."
    except Exception as e:
        return f"⚠️ Connection error: {e}"

# --- KEYBOARDS ---
main_menu = [['🎬 Single Video','📂 Video List'], ['🆓 Free Channel','💎 Paid Channel'], ['👥 My Referrals']]
admin_menu = [['📊 Bot Stats','📢 Broadcast'], ['👥 User Count','📝 User List'], ['🔙 Back to Menu']]

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_data('users.json', {})
    user_id = str(user.id)
    ref_by = context.args[0] if context.args else None

    if user_id not in users:
        users[user_id] = {"ref":0,"last":0,"username":user.username or "N/A","name":user.first_name,"referred_by": ref_by}
        if ref_by and ref_by in users and ref_by!=user_id:
            users[ref_by]["ref"] +=1
        save_data('users.json',users)

    # --- START MESSAGE ONLY ---
    start_message = (
        "🎬 Welcome to your Personal Video Finder Bot! 🎥\n\n"
        "Here, you can explore and get access to videos in any category you want. "
        "Just type your preferred category, and the bot will provide a unique shortened link instantly.\n\n"
        "✨ Features:\n"
        "- Select a type: Single Video 🎬, Video List 📂, Free Channel 🆓, Paid Channel 💎\n"
        "- Enter any category you like, and get a custom link 🔗\n"
        "- Referral system: Invite friends to unlock special rewards! 👥\n"
        "- Easy-to-use menu with buttons for fast navigation\n"
        "- Admin monitored and fully secure\n\n"
        "🚀 How it works:\n"
        "1. Tap a menu button\n"
        "2. Type the category you are interested in\n"
        "3. Receive a unique link instantly\n"
        "4. Share your referral link to earn bonuses!\n\n"
        "💡 Note:\n"
        "- Each link is unique and generated just for you\n"
        "- Wait a few seconds between requests to avoid spam\n"
        "- Your privacy and security are always protected\n\n"
        "Enjoy your personalized video experience! 🎉"
    )

    await update.message.reply_text(start_message)

    # --- MENU BUTTONS ---
    await update.message.reply_text(
        f"👋 Welcome, {user.first_name}! Choose an option from the menu below:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    users = load_data('users.json', {})
    step = context.user_data.get("step")

    # --- ADMIN ACTIONS ---
    if int(user_id)==ADMIN_ID:
        if text=='📊 Bot Stats':
            total_users=len(users)
            total_ref=sum(u.get("ref",0) for u in users.values())
            await update.message.reply_text(f"📊 Total Users: {total_users}\n🤝 Total Referrals: {total_ref}")
            return
        elif text=='👥 User Count':
            await update.message.reply_text(f"👥 Total Users: {len(users)}")
            return
        elif text=='📝 User List':
            msg="📝 **User List:**\n"
            for uid,info in list(users.items())[-50:]:
                name = info.get('name','N/A')
                username = info.get('username','N/A')
                msg+=f"• {name} (@{username}) | `{uid}`\n"
            await update.message.reply_text(msg,parse_mode="Markdown")
            return
        elif text=='📢 Broadcast':
            context.user_data["step"]="broadcast"
            await update.message.reply_text("Send broadcast message:",reply_markup=ReplyKeyboardRemove())
            return
        elif step=="broadcast":
            for uid in users.keys():
                try: await context.bot.send_message(chat_id=uid,text=text)
                except: pass
            await update.message.reply_text("✅ Broadcast sent!",reply_markup=ReplyKeyboardMarkup(admin_menu,resize_keyboard=True))
            context.user_data["step"]=None
            return

    # --- USER CATEGORY STEP ---
    if step=="category":
        now=time.time()
        if now - users.get(user_id,{}).get("last",0)<5:
            await update.message.reply_text("⚠️ Please wait 5 seconds!",reply_markup=ReplyKeyboardMarkup(main_menu,resize_keyboard=True))
            context.user_data["step"]=None
            return

        counter=load_data('counter.json',{"count":0})
        code=generate_code(counter["count"])
        short_url=shorten_link(f"https://instagram.com/{code}")
        counter["count"]+=1

        if user_id in users: users[user_id]["last"]=now
        save_data('counter.json',counter)
        save_data('users.json',users)

        await update.message.reply_text(
            f"✅ Category: {text}\n🔗 Your Link: {short_url}",
            reply_markup=ReplyKeyboardMarkup(main_menu,resize_keyboard=True)
        )
        context.user_data["step"]=None
        return

    # --- MENU SELECTION ---
    if text in ['🎬 Single Video','📂 Video List','🆓 Free Channel','💎 Paid Channel']:
        context.user_data["step"]="category"
        await update.message.reply_text("Please write the category you want:",reply_markup=ReplyKeyboardRemove())
    elif text=='👥 My Referrals':
        u=users.get(user_id,{})
        bot_info=await context.bot.get_me()
        ref_link=f"https://t.me/{bot_info.username}?start={user_id}"
        await update.message.reply_text(f"🤝 Referrals: {u.get('ref',0)}\n🔗 Your Referral Link:\n{ref_link}")
    elif text=='🔙 Back to Menu':
        await update.message.reply_text("Main Menu:",reply_markup=ReplyKeyboardMarkup(main_menu,resize_keyboard=True))

# --- ADMIN PANEL ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id==ADMIN_ID:
        await update.message.reply_text("🛠 Admin Panel:",reply_markup=ReplyKeyboardMarkup(admin_menu,resize_keyboard=True))
    else:
        await update.message.reply_text("❌ You are not admin.",reply_markup=ReplyKeyboardMarkup(main_menu,resize_keyboard=True))

# --- MAIN ---
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("admin",admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_message))
    app.run_polling()

if __name__=="__main__":
    main()
