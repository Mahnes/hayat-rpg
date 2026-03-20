import json, os, random
from datetime import datetime
import matplotlib.pyplot as plt

DATA_FILE = "rpg_data.json"

# ---------------- LOAD & SAVE ----------------
def load():
    default = {
        "puan": 0,
        "seviye": 1,
        "streak": 0,
        "son_gun": "",
        "zorluk": "orta",
        "gecmis": []
    }

    if not os.path.exists(DATA_FILE):
        return default

    data = json.load(open(DATA_FILE))
    for k, v in default.items():
        if k not in data:
            data[k] = v
    return data

def save(data):
    json.dump(data, open(DATA_FILE, "w"))
    bulut()

# ---------------- BİLDİRİM ----------------
def bildirim(m):
    os.system(f'termux-notification --title "HAYAT" --content "{m}" --vibrate 1000 --sound')

# ---------------- BULUT ----------------
def bulut():
    os.system("git add .")
    os.system('git commit -m "auto save"')
    os.system("git push origin main")

# ---------------- AI GÖREV ----------------
def ai(data):
    z = data["zorluk"]

    spor = ["15 şınav", "20 squat", "10 dk ip atla"]
    zihin = ["30 dk kitap oku", "1 saat ders çalış"]
    disiplin = ["soğuk duş al", "telefonu 1 saat bırak", "odayı düzenle"]

    # AI: alışkanlıklarına göre görev seçimi (basit mantık)
    if z == "kolay":
        sec = random.choice(spor)
        puan = 10
    elif z == "orta":
        sec = random.choice(spor + zihin)
        puan = 20
    else:
        sec = random.choice(spor + zihin + disiplin)
        puan = 35

    return (sec, puan)

# ---------------- GÖREV ----------------
def gorev_al(data):
    g = ai(data)
    print(f"\n🎯 {g[0]} (+{g[1]} puan)")
    bildirim(g[0])
    return g

def tamamla(g):
    data = load()
    bugun = datetime.now().strftime("%Y-%m-%d")

    if data["son_gun"] != bugun:
        data["streak"] += 1
        data["son_gun"] = bugun

    data["puan"] += g[1]

    # Otomatik zorluk artışı mantığı
    if data["streak"] % 5 == 0 and data["zorluk"] != "zor":
        if data["zorluk"] == "kolay":
            data["zorluk"] = "orta"
        elif data["zorluk"] == "orta":
            data["zorluk"] = "zor"
        bildirim(f"⚡ Zorluk seviyesi {data['zorluk']} oldu!")

    if data["puan"] >= data["seviye"] * 100:
        data["seviye"] += 1
        bildirim("LEVEL ATLADIN 🔥")

    data["gecmis"].append({
        "tarih": bugun,
        "puan": g[1]
    })

    save(data)
    print("✅ Tamamlandı")

# ---------------- GRAFİK ----------------
def grafik(tip):
    data = load()
    gecmis = data["gecmis"]

    if not gecmis:
        print("Veri yok")
        return

    sayac = {}
    for g in gecmis:
        t = g["tarih"]
        if tip == "gun":
            key = t
        elif tip == "hafta":
            key = t[:7] + "-W"
        else:
            key = t[:7]

        sayac[key] = sayac.get(key, 0) + g["puan"]

    x = list(sayac.keys())
    y = list(sayac.values())

    plt.bar(x, y)
    plt.title(f"{tip.upper()} GRAFİK")
    plt.xticks(rotation=45)
    plt.show()

# ---------------- CHALLENGE ----------------
def challenge():
    c = [
        ("5 gün görev yap", 100),
        ("200 puan kas", 150)
    ]
    ch = random.choice(c)
    print(f"🏆 {ch[0]} (+{ch[1]} puan)")

# ---------------- ZORLUK ----------------
def zorluk():
    data = load()
    z = input("kolay / orta / zor: ")
    if z in ["kolay","orta","zor"]:
        data["zorluk"] = z
        save(data)

# ---------------- MENÜ ----------------
def menu():
    task = None

    while True:
        print("\n=== HAYAT ===")
        print("1 görev al")
        print("2 tamamla")
        print("3 durum")
        print("4 zorluk")
        print("5 günlük grafik")
        print("6 haftalık grafik")
        print("7 aylık grafik")
        print("8 challenge")
        print("9 çık")

        s = input(">> ")

        if s=="1":
            task = gorev_al(load())
        elif s=="2":
            if task:
                tamamla(task)
                task = None
            else:
                print("Önce görev al")
        elif s=="3":
            print(load())
        elif s=="4":
            zorluk()
        elif s=="5":
            grafik("gun")
        elif s=="6":
            grafik("hafta")
        elif s=="7":
            grafik("ay")
        elif s=="8":
            challenge()
        elif s=="9":
            break

menu()
