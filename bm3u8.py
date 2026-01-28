import requests
import re
import base64
import os
from bs4 import BeautifulSoup

BASE_URL = "https://v5on.site"
TARGET_URL = "https://v5on.site?cat=all"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": BASE_URL,
}

os.makedirs("channels", exist_ok=True)

resp = requests.get(TARGET_URL, headers=HEADERS)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# استخراج كل روابط play.php?id= مع اسم القناة
channels = []
for a in soup.find_all('a', href=True):
    if 'play.php?id=' in a['href']:
        channel_id = a['href'].split("id=")[1].split("&")[0]
        # اسم القناة من النص أو من بطاقة القناة
        name_tag = a.find(['h5','h6','div','span'])
        name = name_tag.get_text(strip=True) if name_tag else f"Channel_{channel_id}"
        # إزالة أي أحرف غير صالحة في اسم الملف
        safe_name = re.sub(r'[^a-zA-Z0-9_\- ]', '', name)
        channels.append((channel_id, safe_name))

for channel_id, channel_name in channels:
    api_url = f"{BASE_URL}/api/playlist.php?id={channel_id}"
    r = requests.get(api_url, headers=HEADERS)
    r.raise_for_status()
    data = r.text

    segments = re.findall(r'segment\.php\?u=([A-Za-z0-9=]+)', data)
    if not segments:
        continue

    out_file = f"channels/{channel_name}.m3u8"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        for i, s in enumerate(segments):
            s += "=" * (-len(s) % 4)
            try:
                ts_url = base64.b64decode(s).decode()
                f.write(f"#EXTINF:10,{channel_name}_{i}\n")
                f.write(ts_url + "\n")
            except:
                continue
    print(f"[OK] Generated {out_file}")
