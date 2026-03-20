import os
import subprocess
import time
import re

# Tarama yapılacak IP aralığı
network_range = "192.168.1.0/24"

def scan_network():
    # nmap kullanarak cihazları tarıyoruz
    try:
        output = subprocess.check_output(
            ["nmap", "-sn", network_range], universal_newlines=True
        )
    except FileNotFoundError:
        print("Lütfen önce 'nmap' yükleyin: pkg install nmap")
        return []

    devices = []
    lines = output.split("\n")
    current_ip = ""
    for line in lines:
        if "Nmap scan report for" in line:
            # IP veya hostname al
            parts = line.split("for")
            current_ip = parts[1].strip()
        if "MAC Address" in line:
            mac_info = line.split("MAC Address:")[1].strip()
            devices.append((current_ip, mac_info))
            current_ip = ""
        elif current_ip != "":
            # MAC yoksa IP ve hostname
            devices.append((current_ip, "Unknown MAC"))
            current_ip = ""
    return devices

def main():
    print("=== TERMUX WIFI RADAR ===")
    print(f"Ağ aralığı: {network_range}")
    while True:
        devices = scan_network()
        os.system("clear")
        print("Bağlı cihazlar:")
        for ip, mac in devices:
            # MAC'den üretici tahmini
            vendor = mac.split("(")[-1].replace(")", "") if "(" in mac else "Unknown"
            print(f"{ip}  |  {vendor}")
        print("\nYenilemek için 10 saniye bekleniyor...")
        time.sleep(10)

if __name__ == "__main__":
    main()
