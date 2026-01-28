import requests
from bs4 import BeautifulSoup

BASE_URL = "https://v5on.site/index.php"
CATEGORY_ID = "416"   # ← غيّر هنا رقم الباقة
OUTPUT_FILE = "test.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

print(f"[+] استخراج باقة cat={CATEGORY_ID}")

url = f"{BASE_URL}?cat={CATEGORY_ID}"
resp = requests.get(url, headers=HEADERS, timeout=15)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

channels = []

for a in soup.select("a.channel-card"):
    href = a.get("href", "")
    if "play.php?id=" not in href:
        continue

    ch_id = href.split("id=")[-1].strip()
    name_tag = a.select_one(".card-info h4")
    name = name_tag.text.strip() if name_tag else f"Channel {ch_id}"

    logo_tag = a.select_one(".card-thumbnail img")
    logo = logo_tag["src"] if logo_tag else ""

    channel_url = f"https://v5on.site/{href}"

    channels.append((ch_id, name, logo, channel_url))

# كتابة M3U
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch_id, name, logo, channel_url in channels:
        f.write(
            f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="TEST",{name}\n'
        )
        f.write(channel_url + "\n")

print(f"✔ تم استخراج {len(channels)} قناة → {OUTPUT_FILE}")
