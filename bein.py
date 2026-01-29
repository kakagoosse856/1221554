import requests
import os
import re

# =====================
# مصادر القنوات
# =====================
SOURCES = [
    "https://raw.githubusercontent.com/la22lo/sports/93071e41b63c35c60a18631e3dc8d9dc2818ae61/futbol.m3u",
    "https://raw.githubusercontent.com/a7shk1/m3u-broadcast/bddbb1a1a24b50ee3e269c49eae50bef5d63894b/bein.m3u",
    "https://raw.githubusercontent.com/mdarif2743/Cmcl-digital/e3f60bd80f189c679415e6b2b51d79a77440793a/Cmcl%20digital",
     "https://github.com/fareskhaled505/Me/blob/74e43c8d7dac1e6628ec0174bdc2bd384ea7a55a/bein.m3u8",
     "https://raw.githubusercontent.com/theariatv/theariatv.github.io/e5c3ce629db976e200a1b4f4ece176b04e829c79/aria.m3u"
     "https://raw.githubusercontent.com/Yusufdkci/iptv/refs/heads/main/liste.m3u",
      "https://raw.githubusercontent.com/judy-gotv/iptv/4beaf567d5d056dbe08477a5d15b48c2a2e2dfce/BD.m3u",
      "https://raw.githubusercontent.com/judy-gotv/iptv/4beaf567d5d056dbe08477a5d15b48c2a2e2dfce/world.m3u",
      "https://raw.githubusercontent.com/judy-gotv/iptv/4beaf567d5d056dbe08477a5d15b48c2a2e2dfce/UDPTV.m3u",
      "https://raw.githubusercontent.com/judy-gotv/iptv/4beaf567d5d056dbe08477a5d15b48c2a2e2dfce/tubi_playlist.m3u",
      "https://raw.githubusercontent.com/lusianaputri/lusipunyalu/d5d1b411b6020519501860ab1f2dda128a033885/b.txt",
      "https://github.com/FunctionError/PiratesTv/blob/97aadde222f09567d5f03de4574cae49c3cf90ab/combined_playlist.m3u",
       "https://raw.githubusercontent.com/bugsfreeweb/LiveTVCollector/a10774f0e8c35443bc9237e2a48e9c0988ff9e0f/LiveTV/India/LiveTV.m3u",
       "https://raw.githubusercontent.com/sxtv2323/sxtv-iptv11/refs/heads/main/TOD%20.m3u",
       "https://raw.githubusercontent.com/raid35/channel-links/refs/heads/main/ALWAN.m3u",
    
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
        lines = requests.get(src, timeout=20).text.splitlines()
    except Exception as e:
        print(f"[ERROR] {e}")
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
        name_match = re.search(r'#EXTINF:-1.*?,(.*)', line)
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
