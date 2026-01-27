import requests
from bs4 import BeautifulSoup

URL = "https://v5on.site/index.php?cat=29"
OUTPUT_FILE = "v5.m3u"

resp = requests.get(URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")
channels = []

for a in soup.find_all("a", class_="channel-card"):
    href = a.get("href", "")
    if "play.php?id=" in href:
        channel_id = href.split("play.php?id=")[-1]
        h4 = a.find("h4")
        name = h4.text.strip() if h4 else f"Channel {channel_id}"
        channels.append({"name": name, "id": channel_id})

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for ch in channels:
        f.write(f"#EXTINF:-1 tvg-name=\"{ch['name']}\",{ch['name']}\n")
        f.write(f"play.php?id={ch['id']}\n\n")

print(f"تم إنشاء {OUTPUT_FILE} بعدد {len(channels)} قناة.")
