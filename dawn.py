import ast
import json
import re

import requests
import random
import time
import datetime
import urllib3
from PIL import Image
import base64
from io import BytesIO
import ddddocr
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from loguru import logger

KeepAliveURL = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
GetPointURL = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
LoginURL = "https://www.aeropres.in//chromeapi/dawn/v1/user/login/v2"
PuzzleID = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle"

# Membuat sesi permintaan
session = requests.Session()

# Mengatur header umum untuk permintaan
headers = {
    "Content-Type": "application/json",
    "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Priority": "u=1, i",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}


def GetPuzzleID():
    r = session.get(PuzzleID, headers=headers, verify=False).json()
    puzzid = r['puzzle_id']
    return puzzid

# Memeriksa ekspresi captcha
def IsValidExpression(expression):
    # Memeriksa apakah ekspresi adalah kombinasi 6 karakter alfanumerik
    pola = r'^[A-Za-z0-9]{6}$'
    if re.match(pola, expression):
        return True
    return False

# Pengenalan captcha
def RemixCaptacha(base64_image):
    # Mengonversi string Base64 menjadi data biner
    image_data = base64.b64decode(base64_image)
    # Menggunakan BytesIO untuk mengonversi data biner menjadi objek file yang dapat dibaca
    image = Image.open(BytesIO(image_data))
    #####################################
    # Mengonversi gambar ke mode RGB (jika belum)
    image = image.convert('RGB')
    # Membuat gambar baru (latar belakang putih)
    new_image = Image.new('RGB', image.size, 'white')
    # Mendapatkan lebar dan tinggi gambar
    width, height = image.size
    # Memproses setiap piksel
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            # Jika piksel berwarna hitam, simpan; jika tidak, ubah menjadi putih
            if pixel == (48, 48, 48):  # Piksel hitam
                new_image.putpixel((x, y), pixel)  # Simpan piksel hitam asli
            else:
                new_image.putpixel((x, y), (255, 255, 255))  # Ganti dengan putih

    ##################

    # Membuat objek OCR
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocr.set_ranges(0)
    result = ocr.classification(new_image)
    logger.debug(f'[1] Hasil pengenalan captcha: {result}, apakah captcha dapat dihitung {IsValidExpression(result)}',)
    if IsValidExpression(result) == True:
        #rc = eval(result)
        return result


def login(USERNAME, PASSWORD):
    puzzid = GetPuzzleID()
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "logindata": {
            "_v": "1.0.7",
            "datetime": current_time
        },
        "puzzle_id": puzzid,
        "ans": "0"
    }
    # Bagian pengenalan captcha
    refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False).json()
    code = RemixCaptacha(refresh_image['imgBase64'])
    if code:
        logger.success(f'[√] Berhasil mendapatkan hasil captcha {code}',)
        data['ans'] = str(code)
        login_data = json.dumps(data)
        logger.info(f'[2] Data login: {login_data}')
        try:
            r = session.post(LoginURL, login_data, headers=headers, verify=False).json()
            logger.debug(r)
            token = r['data']['token']
            logger.success(f'[√] Berhasil mendapatkan AuthToken {token}')
            return token
        except Exception as e:
            logger.error(f'[x] Captcha salah, coba mendapatkan ulang...')

def KeepAlive(USERNAME, TOKEN):
    data = {"username": USERNAME, "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp", "numberoftabs": 0, "_v": "1.0.7"}
    json_data = json.dumps(data)
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False).json()
    logger.info(f'[3] Menjaga koneksi... {r}')


def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.get(GetPointURL, headers=headers, verify=False).json()
    logger.success(f'[√] Berhasil mendapatkan Point {r}')


def main(USERANEM, PASSWORD):
    TOKEN = ''
    if TOKEN == '':
        while True:
            TOKEN = login(USERANEM, PASSWORD)
            if TOKEN:
                break
    # Inisialisasi penghitung
    count = 0
    max_count = 200  # Setiap 200 kali eksekusi, perbarui TOKEN
    while True:
        try:
            # Jalankan operasi menjaga koneksi dan mendapatkan poin
            KeepAlive(USERANEM, TOKEN)
            GetPoint(TOKEN)
            # Perbarui penghitung
            count += 1
            # Setiap mencapai max_count, dapatkan ulang TOKEN
            if count >= max_count:
                logger.debug(f'[√] Mendapatkan ulang Token...')
                while True:
                    TOKEN = login(USERANEM, PASSWORD)
                    if TOKEN:
                        break
                count = 0  # Reset penghitung
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
