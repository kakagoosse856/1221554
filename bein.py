import requests
import os
import re

M3U_SOURCES = [
    "https://raw.githubusercontent.com/Walid533112/airmax/refs/heads/main/airmax.m3u",
    "https://raw.githubusercontent.com/Yusufdkci/iptv/71fabe363ebf0c3d46ae0ce69f8e3202164b7edc/liste.m3u"
]

CHANNEL_MAP = {
    "beIN Sports 1 HD": ["bein1", "bn1", "/1", "sport1"],
    "beIN Sports 2 HD": ["bein2", "bn2", "/2", "sport2"],
    "beIN Sports 3 HD": ["bein3", "bn3", "/3", "sport3"],
    "beIN Sports ": ["bein", "bn", "/1", "sport4"],
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
        if line.startswith("#EXTINF"):
            if i + 1 >= len(lines):
                continue

            url = lines[i + 1].strip()
            url_low = url.lower()

            for ch, keys in CHANNEL_MAP.items():
                if any(k in url_low for k in keys):
                    try:
                        r = requests.head(url, timeout=6, allow_redirects=True)
                        if r.status_code == 200:
                            found[ch].add(url)
                            print(f"[OK] {ch}")
                    except:
                        pass

# إنشاء الملف
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch, urls in found.items():
        if not urls:
            print(f"[MISS] {ch}")
            continue
        for url in sorted(urls):
            f.write(f"#EXTINF:-1,{ch}\n")
            f.write(url + "\n")

print(f"[DONE] تم إنشاء الملف النهائي: {OUTPUT_FILE}")
