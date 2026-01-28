import requests
import re
import base64
import os
from bs4 import BeautifulSoup

BASE_URL = "https://v5on.site"
TARGET_URL = "https://v5on.site/index.php?cat=2136"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": BASE_URL,
}

os.makedirs("channels", exist_ok=True)

print("[INFO] Fetching channel list...")
resp = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# استخراج كل القنوات (ID + اسم القناة)
channels = []
for a in soup.find_all('a', href=True):
    if 'play.php?id=' in a['href']:
        channel_id = a['href'].split("id=")[1].split("&")[0]
        # الحصول على اسم القناة
        name_tag = a.find(['h5','h6','div','span'])
        name = name_tag.get_text(strip=True) if name_tag else f"Channel_{channel_id}"
        safe_name = re.sub(r'[^a-zA-Z0-9_\- ]', '', name)  # اسم صالح كملف
        channels.append((channel_id, safe_name))

print(f"[INFO] Found {len(channels)} channels.")

for channel_id, channel_name in channels:
    try:
        api_url = f"{BASE_URL}/api/playlist.php?id={channel_id}"
        r = requests.get(api_url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.text

        segments = re.findall(r'segment\.php\?u=([A-Za-z0-9=]+)', data)
        if not segments:
            print(f"[WARN] No segments found for {channel_name}")
            continue

        out_file = f"channels/{channel_name}.m3u8"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n#EXT-X-VERSION:3\n")
            for i, s in enumerate(segments):
                s += "=" * (-len(s) % 4)  # تصحيح padding
                try:
                    ts_url = base64.b64decode(s).decode()
                    f.write(f"#EXTINF:10,{channel_name}_{i}\n")
                    f.write(ts_url + "\n")
                except Exception as e:
                    print(f"[ERROR] Segment decode failed: {e}")
        print(f"[OK] Generated {out_file}")
    except Exception as e:
        print(f"[ERROR] Failed channel {channel_name}: {e}")
