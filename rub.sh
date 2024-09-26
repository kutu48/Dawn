#!/bin/bash

# Memeriksa apakah skrip dijalankan sebagai pengguna root
if [ "$(id -u)" != "0" ]; then
    echo "Skrip ini harus dijalankan dengan hak akses pengguna root."
    echo "Coba gunakan perintah 'sudo -i' untuk beralih ke pengguna root, lalu jalankan skrip ini lagi."
    exit 1
fi

# Memeriksa dan menginstal Node.js dan npm
function install_nodejs_and_npm() {
    if command -v node > /dev/null 2>&1; then
        echo "Node.js sudah diinstal"
    else
        echo "Node.js belum diinstal, sedang menginstal..."
        curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi

    if command -v npm > /dev/null 2>&1; then
        echo "npm sudah diinstal"
    else
        echo "npm belum diinstal, sedang menginstal..."
        sudo apt-get install -y npm
    fi
}

# Memeriksa dan menginstal PM2
function install_pm2() {
    if command -v pm2 > /dev/null 2>&1; then
        echo "PM2 sudah diinstal"
    else
        echo "PM2 belum diinstal, sedang menginstal..."
        npm install pm2@latest -g
    fi
}


# Fungsi instalasi node
function install_node() {
    install_nodejs_and_npm
    install_pm2

    pip3 install pillow
    pip3 install ddddocr
    pip3 install requests
    pip3 install loguru


    # Mendapatkan nama pengguna
    read -r -p "Masukkan email: " DAWNUSERNAME
    export DAWNUSERNAME=$DAWNUSERNAME

    # Mendapatkan kata sandi
    read -r -p "Masukkan kata sandi: " DAWNPASSWORD
    export DAWNPASSWORD=$DAWNPASSWORD

    echo $DAWNUSERNAME:$DAWNPASSWORD > password.txt

    wget -O dawn.py https://raw.githubusercontent.com/b1n4he/DawnAuto/main/dawn.py
    # Memperbarui dan menginstal perangkat lunak yang diperlukan
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl iptables build-essential git wget jq make gcc nano tmux htop nvme-cli pkg-config libssl-dev libleveldb-dev tar clang bsdmainutils ncdu unzip libleveldb-dev lz4 snapd

    pm2 start dawn.py
}

# Menu utama
function main_menu() {
    while true; do
        clear
        cat << EOF
_________________________
< Skrip Dawn otomatis (versi VPS luar negeri), dari Twitter @oxbaboon >
< Open-source gratis, jika ada yang meminta biaya langsung saja lapor 🤌 >
-------------------------
        \   ^__^
        \  (oo)\_______
            (__)\       )\/\/
                ||----w |
                ||     ||
EOF
        echo "Untuk keluar dari skrip, tekan ctrl + c pada keyboard."
        echo "Pilih tindakan yang ingin dilakukan:"
        echo "1. Instal Node"
        read -p "Masukkan pilihan: " OPTION

        case $OPTION in
        1) install_node ;;
        *) echo "Pilihan tidak valid." ;;
        esac
        echo "Tekan sembarang tombol untuk kembali ke menu utama..."
        read -n 1
    done
    
}

# Tampilkan menu utama
main_menu
