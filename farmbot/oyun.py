import sqlite3, time, random
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8735720097:AAFpD-okpE6vHOlHxr1lAO5jlQqSZLwp5j0"

# Veritabanı
conn = sqlite3.connect("farm.db", check_same_thread=False)
c = conn.cursor()

# Tablolar
c.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    money INT,
    rod_level INT,
    pickaxe_level INT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS fields(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT,
    crop TEXT,
    plant_time INT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS inventory(
    user_id INT,
    item TEXT,
    amount INT
)""")
conn.commit()

# Tarla, Balık, Maden, Ürün süreleri
crops = {"🌾 Buğday":20, "🥔 Patates":35, "🥕 Havuç":30}
fish_levels = {
    1:["🐟 Sardalya"],
    2:["🐟 Sardalya","🐠 Somon"],
    3:["🐟 Sardalya","🐠 Somon","🦈 Köpekbalığı"]
}
ores_levels = {
    1:["🪨 Taş"],
    2:["🪨 Taş","⛓ Demir"],
    3:["🪨 Taş","⛓ Demir","🥇 Altın"]
}

# Shop
shop_items = {
    "Tarla":50,
    "🌾 Buğday Tohumu":10,
    "🥔 Patates Tohumu":10,
    "🥕 Havuç Tohumu":10,
    "Gübre":15,
    "🐔 Pet Tavuk":200,
    "🐄 Pet İnek":500,
    "Olta Seviye 2":300,
    "Olta Seviye 3":600,
    "Kazma Seviye 2":300,
    "Kazma Seviye 3":600
}

# Menüler
main_menu = ReplyKeyboardMarkup([
    ["🌾 Tarla","🏪 Pazar"],
    ["🎣 Balık","⛏ Maden"],
    ["🎒 Envanter","👤 Profil"]
],resize_keyboard=True)

back = ReplyKeyboardMarkup([["🔙 Geri"]],resize_keyboard=True)

# Kullanıcı durumu
user_state = {}  # ne yapacağını tutacak (plant vb)
selected_field = {} # seçilen tarla

# Yardımcı fonksiyonlar
def add_item(uid,item,amount=1):
    c.execute("SELECT amount FROM inventory WHERE user_id=? AND item=?",(uid,item))
    d=c.fetchone()
    if d:
        c.execute("UPDATE inventory SET amount=amount+? WHERE user_id=? AND item=?",(amount,uid,item))
    else:
        c.execute("INSERT INTO inventory VALUES(?,?,?)",(uid,item,amount))
    conn.commit()

def get_money(uid):
    c.execute("SELECT money FROM users WHERE user_id=?",(uid,))
    d=c.fetchone()
    return d[0] if d else 0

def get_user(uid):
    c.execute("SELECT * FROM users WHERE user_id=?",(uid,))
    return c.fetchone()

def create_field(uid):
    # 3 tarla ile başlasın
    for _ in range(3):
        c.execute("INSERT INTO fields(user_id,crop,plant_time) VALUES(?,?,?)",(uid,None,0))
    conn.commit()

# Başlat
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not get_user(uid):
        c.execute("INSERT INTO users VALUES(?,?,?,?)",(uid,200,1,1))
        conn.commit()
        create_field(uid)
    await update.message.reply_text("🌱 Çiftliğe hoş geldin!",reply_markup=main_menu)

# Profil
async def profile(update:Update,context:ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    user=get_user(uid)
    txt=f"👤 Profil\n💰 Para: {user[1]}\n🎣 Olta: {user[2]}\n⛏ Kazma: {user[3]}"
    await update.message.reply_text(txt,reply_markup=main_menu)

# Envanter
async def inventory(update:Update,context:ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    c.execute("SELECT item,amount FROM inventory WHERE user_id=?",(uid,))
    items=c.fetchall()
    if not items:
        txt="🎒 Envanter boş"
    else:
        txt="🎒 Envanter\n"
        for i in items:
            txt+=f"{i[0]} x{i[1]}\n"
    await update.message.reply_text(txt,reply_markup=main_menu)

# Pazar
async def market(update:Update,context:ContextTypes.DEFAULT_TYPE):
    kb=[]
    row=[]
    for item,price in shop_items.items():
        row.append(f"{item} {price}💰")
        if len(row)==2:
            kb.append(row)
            row=[]
    if row: kb.append(row)
    kb.append(["🔙 Geri"])
    await update.message.reply_text("🏪 Pazar",reply_markup=ReplyKeyboardMarkup(kb,resize_keyboard=True))

# Tarla
async def tarla(update:Update,context:ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    c.execute("SELECT * FROM fields WHERE user_id=?",(uid,))
    f=c.fetchall()
    if not f:
        await update.message.reply_text("Tarlan yok. Pazardan satın al.",reply_markup=main_menu)
        return
    kb,row=[],[]
    for field in f:
        fid=field[0]
        if field[2]==None:
            txt=f"⬜ {fid}"
        else:
            crop=field[2]
            txt=f"🌱 {fid} {crop}"
        row.append(txt)
        if len(row)==3: kb.append(row); row=[]
    if row: kb.append(row)
    kb.append(["🔙 Geri"])
    await update.message.reply_text("🌾 Tarlalar",reply_markup=ReplyKeyboardMarkup(kb,resize_keyboard=True))

# Balık
async def fish_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    rod=get_user(uid)[2]
    fish_list=[]
    for lvl in range(1,rod+1):
        fish_list+=fish_levels[lvl]
    f=random.choice(fish_list)
    add_item(uid,f)
    await update.message.reply_text(f"🎣 {f} tuttun!",reply_markup=main_menu)

# Madencilik
async def mine(update:Update,context:ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id
    pick=get_user(uid)[3]
    ores=[]
    for lvl in range(1,pick+1):
        ores+=ores_levels[lvl]
    o=random.choice(ores)
    add_item(uid,o)
    await update.message.reply_text(f"⛏ {o} çıkardın!",reply_markup=main_menu)

# Ekim menüsü
async def plant_menu(update,uid):
    kb=ReplyKeyboardMarkup([
        ["🌾 Buğday","🥔 Patates"],
        ["🥕 Havuç"],
        ["🔙 Geri"]
    ],resize_keyboard=True)
    await update.message.reply_text("Ne ekmek istiyorsun?",reply_markup=kb)

# Ana handler
async def handle(update:Update,context:ContextTypes.DEFAULT_TYPE):
    txt=update.message.text
    uid=update.effective_user.id

    if txt=="🌾 Tarla": await tarla(update,context); return
    if txt=="🏪 Pazar": await market(update,context); return
    if txt=="🎣 Balık": await fish_cmd(update,context); return
    if txt=="⛏ Maden": await mine(update,context); return
    if txt=="🎒 Envanter": await inventory(update,context); return
    if txt=="👤 Profil": await profile(update,context); return
    if txt=="🔙 Geri": await update.message.reply_text("Ana Menü",reply_markup=main_menu); return

    # Pazar alımı
    for item in shop_items:
        if txt.startswith(item):
            price=int(shop_items[item])
            if get_money(uid)>=price:
                c.execute("UPDATE users SET money=money-? WHERE user_id=?",(price,uid))
                # Olta/Kazma seviyeleri
                if "Olta" in item:
                    lvl=int(item[-1])
                    c.execute("UPDATE users SET rod_level=? WHERE user_id=?",(lvl,uid))
                elif "Kazma" in item:
                    lvl=int(item[-1])
                    c.execute("UPDATE users SET pickaxe_level=? WHERE user_id=?",(lvl,uid))
                else:
                    add_item(uid,item)
                conn.commit()
                await update.message.reply_text(f"{item} satın alındı!",reply_markup=main_menu)
            else:
                await update.message.reply_text("💰 Para yok!",reply_markup=main_menu)
            return

    # Tarla grid seçimi
    if txt.startswith("⬜") or txt.startswith("🌱"):
        fid=int(txt.split(" ")[1])
        selected_field[uid]=fid
        c.execute("SELECT crop,plant_time FROM fields WHERE id=?",(fid,))
        data=c.fetchone()
        if data[0]==None:
            user_state[uid]="plant"
            await plant_menu(update,uid)
        else:
            crop=data[0]
            plant_time=data[1]
            if time.time()-plant_time>crops[crop]:
                add_item(uid,crop)
                c.execute("UPDATE fields SET crop=NULL,plant_time=0 WHERE id=?",(fid,))
                conn.commit()
                await update.message.reply_text("🌾 Hasat edildi!",reply_markup=main_menu)
            else:
                await update.message.reply_text("🌱 Henüz büyümedi.",reply_markup=main_menu)
        return

    # Ekim
    if uid in user_state and user_state[uid]=="plant":
        fid=selected_field[uid]
        if txt in crops:
            c.execute("UPDATE fields SET crop=?,plant_time=? WHERE id=?",(txt,time.time(),fid))
            conn.commit()
            user_state.pop(uid)
            await update.message.reply_text(f"🌱 {txt} ekildi!",reply_markup=main_menu)

# Bot başlat
app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT,handle))
app.run_polling()
