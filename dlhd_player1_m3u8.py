import re
import requests
from datetime import datetime

# الرابط الأصلي
BASE_URL = "https://dokko1new.dvalna.ru/dokko1/premium91/mono.css"

# Headers لتجنب 404
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://dokko1new.dvalna.ru/",
    "Accept": "text/css,*/*;q=0.1",
}

# جلب ملف CSS
response = requests.get(BASE_URL, headers=HEADERS)
if response.status_code != 200:
    raise Exception(f"فشل تحميل الملف: {response.status_code}")

css_content = response.text

# استخراج روابط m3u8, ts, key
m3u8_links = re.findall(r'https?://[^;\s]+\.m3u8\?[^;\s]+', css_content)
ts_links = re.findall(r'https?://[^;\s]+\.ts\?[^;\s]+', css_content)
key_links = re.findall(r'https?://[^;\s]+/key/[^;\s]+', css_content)

# إعداد ملف M3U النهائي
playlist_content = "#EXTM3U\n# Generated on {}\n\n".format(datetime.utcnow().isoformat())

# إضافة كل Players (1 → 5)
for player_num in range(1, 6):
    playlist_content += f"# Player {player_num}\n"
    
    # روابط m3u8
    for m3u8 in m3u8_links:
        playlist_content += f"#EXTINF:-1,Player {player_num}\n{m3u8}\n"
    
    # روابط ts (اختياري حسب دعم Player)
    for ts in ts_links:
        playlist_content += f"#EXTINF:-1,Player {player_num} TS\n{ts}\n"
    
    # روابط key (لـ AES-128)
    for key in key_links:
        playlist_content += f"#EXT-X-KEY:METHOD=AES-128,URI=\"{key}\"\n"

# حفظ الملف محليًا
with open("final_playlist.m3u8", "w", encoding="utf-8") as f:
    f.write(playlist_content)

print("تم إنشاء الملف بنجاح: dlhd_player1_m3u8")
