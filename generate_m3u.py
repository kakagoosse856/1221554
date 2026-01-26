import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HTML_URL = "https://raw.githubusercontent.com/kakagoosse856/1221554/main/v5.html"
BASE_PLAY_URL = "https://v5on.site/play.php?id="

headers = {
    "User-Agent": "Mozilla/5.0"
}

resp = requests.get(HTML_URL, headers=headers)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

channels = []

for a in soup.select("a.channel-card"):
    href = a.get("href", "")
    if "id=" not in href:
        continue

    channel_id = href.split("id=")[-1]

    name_tag = a.select_one("h4")
    name = name_tag.text.strip() if name_tag else f"Channel {channel_id}"

    img_tag = a.select_one("img")
    logo = img_tag["src"] if img_tag and img_tag.get("src") else ""

    play_url = BASE_PLAY_URL + channel_id

    channels.append({
        "id": channel_id,
        "name": name,
        "logo": logo,
        "url": play_url
    })

# توليد M3U
with open("v5.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for ch in channels:
        f.write(
            f'#EXTINF:-1 tvg-id="{ch["id"]}" '
            f'tvg-name="{ch["name"]}" '
            f'tvg-logo="{ch["logo"]}" '
            f'group-title="beIN Sports",{ch["name"]}\n'
        )
        f.write(ch["url"] + "\n\n")

print(f"✔ تم استخراج {len(channels)} قناة بنجاح")
