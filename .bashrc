clear
# Terminal genişliğini al
COLUMNS=$(tput cols)
# Ortalanmış figlet
figlet -f standard MAHNES | awk -v w=$COLUMNS '{printf "%*s\n", (w+length($0))/2, $0}' | lolcat
echo -e "\e[36mTerminaline hoşgeldin! 🚀\e[0m"
alias takip='python ~/takip.py'
