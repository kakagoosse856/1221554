import requests
import os
import re

# =====================
# مصادر القنوات (كل مصدر = سيرفر)
# =====================
SOURCES = [
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/SSULTAN.m3u",
    # أضف مصادر أخرى هنا
]

KEYWORD = "bein"

OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bein_auto.m3u8")

servers = {}

print("[INFO] استخراج قنوات BEIN وترتيبها حسب السيرفر...")

for idx, src in enumerate(SOURCES, start=1):
    server_name = f"SERVER {idx}"
    servers[server_name] = {}

    print(f"[INFO] تحميل {server_name}: {src}")
    try:
        lines = requests.get(src, timeout=20).text.splitlines()
    except Exception as e:
        print(f"[ERROR] {e}")
        continue

    for i, line in enumerate(lines):
        if not line.startswith("#EXTINF") or i + 1 >= len(lines):
            continue

        name = line.lower()
        url = lines[i + 1].strip()
        url_low = url.lower()

        if KEYWORD not in name and KEYWORD not in url_low:
            continue

        # استخراج اسم القناة الحقيقي
        num = re.search(r'(?:bein|bn|sport)[^\d]*(\d)', name + url_low)
        if num:
            channel_name = f"beIN Sports {num.group(1)} HD"
        elif "max" in name or "max" in url_low:
            channel_name = "beIN Sports MAX"
        elif "4k" in name or "4k" in url_low:
            channel_name = "beIN Sports 4K"
        else:
            channel_name = "beIN Sports"

        # فحص الرابط
        try:
            r = requests.head(url, timeout=6, allow_redirects=True)
            if r.status_code != 200:
                continue
        except:
            continue

        servers[server_name].setdefault(channel_name, set()).add(url)
        print(f"[OK] {server_name} | {channel_name}")

# =====================
# إنشاء ملف M3U النهائي
# =====================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

    for server, channels in servers.items():
        for ch in sorted(channels.keys()):
            for url in sorted(channels[ch]):
                f.write(
                    f'#EXTINF:-1 group-title="✪ BEIN AUTO | {server}",{ch}\n'
                )
                f.write(url + "\n")

print(f"[DONE] تم إنشاء الباقة: {OUTPUT_FILE}")
