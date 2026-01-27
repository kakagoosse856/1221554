import requests
from bs4 import BeautifulSoup

# رابط صفحة قنوات beIN
URL = "https://v5on.site/index.php?cat=29"

# ملف الإخراج
OUTPUT_FILE = "bein.m3u"

resp = requests.get(URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

channels = []

# البحث عن كل القنوات
for a in soup.find_all("a", class_="channel-card"):
    href = a.get("href")
    if not href or "play.php?id=" not in href:
        continue
    ch_id = href.split("id=")[-1]
    name_tag = a.find("h4")
    name = name_tag.text.strip() if name_tag else f"beIN {ch_id}"
    logo_tag = a.find("img")
    logo = logo_tag.get("src") if logo_tag else ""
    channels.append({"id": ch_id, "name": name, "logo": logo})

# توليد ملف M3U
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in channels:
        f.write(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}",{ch["name"]}\n')
        f.write(f'play.php?id={ch["id"]}\n')

print(f"Generated {OUTPUT_FILE} with {len(channels)} channels.")
