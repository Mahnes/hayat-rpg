from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import sqlite3, random, asyncio

TOKEN = "8756582628:AAG4KOfqpiV0e_Wkn0aiw5POpg3vqEqngdQ"

conn = sqlite3.connect("casino.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, coin INTEGER)")
conn.commit()

# States  kumar
(
AD_CONFIRM,
DICE_BET,DICE_NUM,
COIN_BET,COIN_CHOICE,
ROULETTE_TYPE,ROULETTE_BET,
BJ_BET,BJ_ACTION,
SLOT_BET,
RPS_BET,RPS_CHOICE
) = range(12)

# Bahis butonları
bet_buttons = ["1","5","10","20","50","75","100","Hepsi"]

def menu():
    return ReplyKeyboardMarkup([
        ["🎰 Slot","🎲 Zar"],
        ["🪙 Yazı Tura","🎡 Rulet"],
        ["🃏 Blackjack","✂️ Taş-Kağıt-Makas"],
        ["💰 Bakiye","📺 Reklam İzle"]
    ],resize_keyboard=True)

def bet_keyboard(coins):
    kb=[]
    for b in bet_buttons:
        if b=="Hepsi":
            kb.append(["Hepsi"])
        elif int(b)<=coins:
            kb.append([b])
    return ReplyKeyboardMarkup(kb,resize_keyboard=True)

def back():
    return ReplyKeyboardMarkup([["🔙 Geri"]],resize_keyboard=True)

def user(id):
    cur.execute("SELECT coin FROM users WHERE id=?",(id,))
    r=cur.fetchone()
    if not r:
        cur.execute("INSERT INTO users VALUES (?,100)",(id,))
        conn.commit()
        return 100
    return r[0]

def add(id,c):
    cur.execute("UPDATE users SET coin=coin+? WHERE id=?",(c,id))
    conn.commit()

# --- START / BALANCE ---
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user(update.effective_user.id)
    await update.message.reply_text("Casino botuna hoşgeldin",reply_markup=menu())

async def balance(update:Update,context:ContextTypes.DEFAULT_TYPE):
    c=user(update.effective_user.id)
    await update.message.reply_text(f"Coin: {c}",reply_markup=menu())

# --- REKLAM ---
async def ad(update:Update,context:ContextTypes.DEFAULT_TYPE):
    kb=ReplyKeyboardMarkup([["Evet","Hayır"]],resize_keyboard=True)
    await update.message.reply_text("Reklam izlemek istiyor musunuz?",reply_markup=kb)
    return AD_CONFIRM

async def ad_confirm(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if update.message.text=="Hayır":
        await update.message.reply_text("İptal.",reply_markup=menu())
        return ConversationHandler.END

    # Evet → reklam link göster ve 30 saniye say
    await update.message.reply_text("Reklam başlıyor...\nhttps://tinyurl.com/3ujsf9hd",reply_markup=None)
    await asyncio.sleep(30)
    add(update.effective_user.id,10)
    await update.message.reply_text("10 coin kazandın!",reply_markup=menu())
    return ConversationHandler.END

# --- SLOT ---
async def slot_start(update,context):
    coins=user(update.effective_user.id)
    await update.message.reply_text("Bahis miktarı?",reply_markup=bet_keyboard(coins))
    return SLOT_BET

async def slot_bet(update,context):
    coins=user(update.effective_user.id)
    if update.message.text=="Hepsi":
        bet=coins
    else:
        bet=int(update.message.text)
    if bet>coins:
        await update.message.reply_text(f"Coin yetersiz. Coin:{coins}",reply_markup=bet_keyboard(coins))
        return SLOT_BET
    symbols = ["🍒","🍋","⭐","💎"]
    s1,s2,s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
    win = bet*5 if s1==s2==s3 else (-bet if s1!=s2 or s2!=s3 else 0)
    add(update.effective_user.id,win)
    await update.message.reply_text(f"{s1} {s2} {s3}\nKazanç: {win}\nCoin:{user(update.effective_user.id)}",reply_markup=menu())
    return ConversationHandler.END

# --- ZAR ---
async def dice_start(update,context):
    coins=user(update.effective_user.id)
    await update.message.reply_text("Bahis miktarı?",reply_markup=bet_keyboard(coins))
    return DICE_BET

async def dice_bet(update,context):
    coins=user(update.effective_user.id)
    if update.message.text=="Hepsi":
        bet=coins
    else:
        bet=int(update.message.text)
    if bet>coins:
        await update.message.reply_text(f"Coin yetersiz. Coin:{coins}",reply_markup=bet_keyboard(coins))
        return DICE_BET
    context.user_data["bet"]=bet
    kb=ReplyKeyboardMarkup([["1","2","3"],["4","5","6"]],resize_keyboard=True)
    await update.message.reply_text("Hangi sayı?",reply_markup=kb)
    return DICE_NUM

async def dice_num(update,context):
    bet=context.user_data["bet"]
    num=int(update.message.text)
    roll=random.randint(1,6)
    win=bet*2 if num==roll else -bet
    add(update.effective_user.id,win)
    await update.message.reply_text(f"Zar: {roll}\nKazanç:{win}\nCoin:{user(update.effective_user.id)}",reply_markup=menu())
    return ConversationHandler.END

# --- YAZI-TURA ---
async def coin_start(update,context):
    coins=user(update.effective_user.id)
    await update.message.reply_text("Bahis?",reply_markup=bet_keyboard(coins))
    return COIN_BET

async def coin_bet(update,context):
    coins=user(update.effective_user.id)
    if update.message.text=="Hepsi":
        bet=coins
    else:
        bet=int(update.message.text)
    context.user_data["bet"]=bet
    kb=ReplyKeyboardMarkup([["Yazı","Tura"]],resize_keyboard=True)
    await update.message.reply_text("Seç:",reply_markup=kb)
    return COIN_CHOICE

async def coin_choice(update,context):
    bet=context.user_data["bet"]
    pick=update.message.text
    result=random.choice(["Yazı","Tura"])
    win=bet*2 if pick==result else -bet
    add(update.effective_user.id,win)
    await update.message.reply_text(f"Sonuç:{result}\nKazanç:{win}\nCoin:{user(update.effective_user.id)}",reply_markup=menu())
    return ConversationHandler.END

# --- RULETTE ---
async def roulette_start(update,context):
    kb=ReplyKeyboardMarkup([["Tek","Çift"],["Kırmızı","Siyah"]],resize_keyboard=True)
    await update.message.reply_text("Bahis türü:",reply_markup=kb)
    return ROULETTE_TYPE

async def roulette_type(update,context):
    context.user_data["rtype"]=update.message.text
    coins=user(update.effective_user.id)
    await update.message.reply_text("Bahis miktarı?",reply_markup=bet_keyboard(coins))
    return ROULETTE_BET

async def roulette_bet(update,context):
    coins=user(update.effective_user.id)
    if update.message.text=="Hepsi":
        bet=coins
    else:
        bet=int(update.message.text)
    rtype=context.user_data["rtype"]
    num=random.randint(0,36)
    color=random.choice(["Kırmızı","Siyah"])
    win=-bet
    if rtype=="Tek" and num%2==1: win=bet*2
    if rtype=="Çift" and num%2==0: win=bet*2
    if rtype=="Kırmızı" and color=="Kırmızı": win=bet*2
    if rtype=="Siyah" and color=="Siyah": win=bet*2
    add(update.effective_user.id,win)
    await update.message.reply_text(f"Sayı:{num} {color}\nKazanç:{win}\nCoin:{user(update.effective_user.id)}",reply_markup=menu())
    return ConversationHandler.END

# --- BLACKJACK ---
async def bj_start(update,context):
    coins=user(update.effective_user.id)
    await update.message.reply_text("Bahis miktarı?",reply_markup=bet_keyboard(coins))
    return BJ_BET

async def bj_bet(update,context):
    coins=user(update.effective_user.id)
    if update.message.text=="Hepsi":
        bet=coins
    else:
        bet=int(update.message.text)
    context.user_data["bet"]=bet
    player=[random.randint(1,11),random.randint(1,11)]
    dealer=[random.randint(1,11),random.randint(1,11)]
    context.user_data["player"]=player
    context.user_data["dealer"]=dealer
    kb=ReplyKeyboardMarkup([["Kart Çek","Dur"]],resize_keyboard=True)
    await update.message.reply_text(f"Sen:{sum(player)} Dealer:{dealer[0]}",reply_markup=kb)
    return BJ_ACTION

async def bj_action(update,context):
    player=context.user_data["player"]
    dealer=context.user_data["dealer"]
    bet=context.user_data["bet"]
    if update.message.text=="Kart Çek":
        player.append(random.randint(1,11))
        if sum(player)>21:
            add(update.effective_user.id,-bet)
            await update.message.reply_text(f"Patladın {sum(player)}",reply_markup=menu())
            return ConversationHandler.END
        kb=ReplyKeyboardMarkup([["Kart Çek","Dur"]],resize_keyboard=True)
        await update.message.reply_text(f"Toplam:{sum(player)}",reply_markup=kb)
        return BJ_ACTION
    while sum(dealer)<17:
        dealer.append(random.randint(1,11))
    ps=sum(player)
    ds=sum(dealer)
    win=0
    if ds>21 or ps>ds: win=bet*2
    elif ps<ds: win=-bet
    add(update.effective_user.id,win)
    await update.message.reply_text(f"Sen:{ps} Dealer:{ds}\nKazanç:{win}\nCoin:{user(update.effective_user.id)}",reply_markup=menu())
    return ConversationHandler.END

# --- TAŞ-KAĞIT-MAKAS ---
async def rps_start(update,context):
    coins=user(update.effective_user.id)
    await update.message.reply_text("Bahis?",reply_markup=bet_keyboard(coins))
    return RPS_BET

async def rps_bet(update,context):
    coins=user(update.effective_user.id)
    if update.message.text=="Hepsi":
        bet=coins
    else:
        bet=int(update.message.text)
    context.user_data["bet"]=bet
    kb=ReplyKeyboardMarkup([["Taş","Kağıt","Makas"]],resize_keyboard=True)
    await update.message.reply_text("Seç:",reply_markup=kb)
    return RPS_CHOICE

async def rps_choice(update,context):
    bet=context.user_data["bet"]
    pick=update.message.text
    comp=random.choice(["Taş","Kağıt","Makas"])
    win=0
    if pick==comp: win=0
    elif (pick=="Taş" and comp=="Makas") or (pick=="Kağıt" and comp=="Taş") or (pick=="Makas" and comp=="Kağıt"): win=bet*2
    else: win=-bet
    add(update.effective_user.id,win)
    await update.message.reply_text(f"Bilgisayar:{comp}\nKazanç:{win}\nCoin:{user(update.effective_user.id)}",reply_markup=menu())
    return ConversationHandler.END

# --- ROUTER ---
async def main_router(update,context):
    t=update.message.text
    if t=="🎲 Zar": return await dice_start(update,context)
    if t=="🪙 Yazı Tura": return await coin_start(update,context)
    if t=="🎡 Rulet": return await roulette_start(update,context)
    if t=="🃏 Blackjack": return await bj_start(update,context)
    if t=="🎰 Slot": return await slot_start(update,context)
    if t=="✂️ Taş-Kağıt-Makas": return await rps_start(update,context)
    if t=="💰 Bakiye": return await balance(update,context)
    if t=="📺 Reklam İzle": return await ad(update,context)

# --- APP ---
app=ApplicationBuilder().token(TOKEN).build()
conv=ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, main_router)],
    states={
        AD_CONFIRM:[MessageHandler(filters.TEXT,ad_confirm)],
        DICE_BET:[MessageHandler(filters.TEXT,dice_bet)],
        DICE_NUM:[MessageHandler(filters.TEXT,dice_num)],
        COIN_BET:[MessageHandler(filters.TEXT,coin_bet)],
        COIN_CHOICE:[MessageHandler(filters.TEXT,coin_choice)],
        ROULETTE_TYPE:[MessageHandler(filters.TEXT,roulette_type)],
        ROULETTE_BET:[MessageHandler(filters.TEXT,roulette_bet)],
        BJ_BET:[MessageHandler(filters.TEXT,bj_bet)],
        BJ_ACTION:[MessageHandler(filters.TEXT,bj_action)],
        SLOT_BET:[MessageHandler(filters.TEXT,slot_bet)],
        RPS_BET:[MessageHandler(filters.TEXT,rps_bet)],
        RPS_CHOICE:[MessageHandler(filters.TEXT,rps_choice)]
    },
    fallbacks=[CommandHandler("start",start)]
)
app.add_handler(CommandHandler("start",start))
app.add_handler(conv)
app.run_polling()
