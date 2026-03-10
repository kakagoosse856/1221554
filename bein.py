import requests
import os
import re

# =====================
# مصادر القنوات
# =====================
SOURCES = [  
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/s1.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser1.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser6.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv4.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv5.m3u8",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv8.m3u8",
       
]

KEYWORD = "bein"
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bein_auto.m3u8")

servers = {}

print("[INFO] استخراج قنوات BEIN وترتيبها حسب السيرفر فقط .m3u8...")

for idx, src in enumerate(SOURCES, start=1):
    server_name = f"SERVER {idx}"
    servers[server_name] = {}

    print(f"[INFO] تحميل {server_name}: {src}")
    try:
        response = requests.get(src, timeout=20)
        response.encoding = 'utf-8'
        lines = response.text.splitlines()
    except Exception as e:
        print(f"[ERROR] فشل تحميل {src}: {e}")
        continue

    for i, line in enumerate(lines):
        if not line.startswith("#EXTINF") or i + 1 >= len(lines):
            continue

        url = lines[i + 1].strip()
        if not url.lower().endswith(".m3u8"):
            continue

        if KEYWORD not in line.lower() and KEYWORD not in url.lower():
            continue

        # استخراج اسم القناة الحقيقي
        name_match = re.search(r'#EXTINF:-?[0-9]*.*?,(.*)', line)
        if name_match:
            channel_name = name_match.group(1).strip()
        else:
            # fallback إذا لم نجد الاسم
            channel_name = "beIN Sports"

        # تحسين أسماء خاصة
        if "max" in channel_name.lower() or "max" in url.lower():
            channel_name = "beIN Sports MAX"
        elif "4k" in channel_name.lower() or "4k" in url.lower():
            channel_name = "beIN Sports 4K"
        elif "hd" in channel_name.lower() or "hd" in url.lower():
            channel_name = "beIN Sports HD"
        elif "sd" in channel_name.lower() or "sd" in url.lower():
            channel_name = "beIN Sports SD"

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
print(f"[INFO] عدد السيرفرات: {len(servers)}")
