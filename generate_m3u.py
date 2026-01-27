import requests
from datetime import datetime

# رابط ملف BEIN.m3u
url = "https://raw.githubusercontent.com/omnixmain/OMNIX-PLAYLIST-ZONE/refs/heads/main/playlist/BEIN.m3u"

# جلب الملف
resp = requests.get(url)
resp.raise_for_status()

lines = resp.text.splitlines()
channels = []

for i, line in enumerate(lines):
    if line.startswith("#EXTINF:"):
        # استخراج الاسم
        name_match = line.split(",")[-1].strip()
        # استخراج id من الرابط الذي يليه
        try:
            url_line = lines[i+1]
            if "play.php?id=" in url_line:
                id_val = url_line.split("play.php?id=")[-1].strip()
                channels.append({"name": name_match, "id": id_val})
        except IndexError:
            continue

# إنشاء ملف M3U
with open("v5.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for ch in channels:
        f.write(f"#EXTINF:-1 tvg-name=\"{ch['name']}\", {ch['name']}\n")
        f.write(f"http://v5on.site/play.php?id={ch['id']}\n\n")

print(f"[{datetime.now()}] تم إنشاء ملف v5.m3u بعدد {len(channels)} قناة.")
