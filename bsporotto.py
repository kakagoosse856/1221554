import requests
from bs4 import BeautifulSoup

URL = "https://v5on.site/index.php?cat=29"  # رابط الصفحة التي تحتوي على القنوات
OUTPUT_FILE = "b11otto.m3u"

resp = requests.get(URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")
channels = []

for a in soup.find_all("a", class_="channel-card"):
    href = a.get("href", "")
    if "play.php?id=" in href:
        channel_id = href.split("play.php?id=")[-1]

        # اسم القناة
        h4 = a.find("h4")
        name = h4.text.strip() if h4 else f"Channel {channel_id}"

        # اللوغو
        img = a.find("img")
        logo = img.get("src") if img else ""

        channels.append({"name": name, "id": channel_id, "logo": logo})

# توليد ملف M3U
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for ch in channels:
        tvg_logo = f' tvg-logo="{ch["logo"]}"' if ch["logo"] else ""
        f.write(f"#EXTINF:-1 tvg-id=\"{ch['id']}\"{tvg_logo},{ch['name']}\n")
        f.write(f"https://v5on.site/play.php?id={ch['id']}\n\n")

print(f"تم إنشاء {OUTPUT_FILE} بعدد {len(channels)} قناة.")
