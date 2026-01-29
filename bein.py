import requests
import os

# =====================
# مصادر M3U (مهم جدًا)
# =====================
SOURCES = [
    "https://raw.githubusercontent.com/Walid533112/airmax/refs/heads/main/airmax.m3u",
    "https://raw.githubusercontent.com/Yusufdkci/iptv/71fabe363ebf0c3d46ae0ce69f8e3202164b7edc/liste.m3u",
    "https://raw.githubusercontent.com/fareskhaled505/Me/74e43c8d7dac1e6628ec0174bdc2bd384ea7a55a/bein.m3u8"
    
]

CHANNEL_MAP = {
    "beIN Sports ": ["bein", "bn", "/1"],
    
}

OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "beinouto.m3u8")

found = {ch: set() for ch in CHANNEL_MAP}

print("[INFO] بدء البحث والتحقق من الروابط...")

for src in SOURCES:
    print(f"[INFO] تحميل المصدر: {src}")
    try:
        lines = requests.get(src, timeout=20).text.splitlines()
    except Exception as e:
        print(f"[ERROR] {e}")
        continue

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF") and i + 1 < len(lines):
            url = lines[i + 1].strip().lower()

            for ch, keys in CHANNEL_MAP.items():
                if any(k in url for k in keys):
                    try:
                        r = requests.head(url, timeout=6, allow_redirects=True)
                        if r.status_code == 200:
                            found[ch].add(lines[i + 1].strip())
                            print(f"[OK] {ch}")
                    except:
                        pass

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch, urls in found.items():
        for url in sorted(urls):
            f.write(f"#EXTINF:-1,{ch}\n{url}\n")

print(f"[DONE] تم إنشاء الملف النهائي: {OUTPUT_FILE}")
