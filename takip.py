import instaloader
import getpass
import os
import time
import random
import subprocess

print("=== Uzun Süreli Takip Kontrol ===")

L = instaloader.Instaloader()

username = input("Kullanıcı adı: ")
session_file = f"{username}.session"

# login
if os.path.exists(session_file):
    try:
        L.load_session_from_file(username, filename=session_file)
    except:
        password = getpass.getpass("Şifre: ")
        L.login(username, password)
        L.save_session_to_file(filename=session_file)
else:
    password = getpass.getpass("Şifre: ")
    L.login(username, password)
    L.save_session_to_file(filename=session_file)

profile = instaloader.Profile.from_username(L.context, username)

def sleep():
    time.sleep(random.randint(5, 10))  # yavaş mod

not_following = []

print("\nTarama başladı...\n")

for f in profile.get_followees():
    try:
        user = instaloader.Profile.from_username(L.context, f.username)

        if not user.follows_viewer:
            not_following.append(f.username)

        sleep()

    except:
        print("Hata... 60 sn bekleniyor")
        time.sleep(60)

# dosyaya kaydet
with open("sonuc.txt", "w") as f:
    for user in not_following:
        f.write(user + "\n")

# BİLDİRİM
subprocess.run([
    "termux-notification",
    "--title", "Takip Listesi Hazır",
    "--content", f"{len(not_following)} kişi seni takip etmiyor"
])

print("\nBitti! sonuc.txt dosyasına kaydedildi.")
