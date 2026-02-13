import requests
from bs4 import BeautifulSoup

# رابط الموقع
URL = "https://v5on.site/index.php?cat=1369"

# اسم ملف M3U الناتج
OUTPUT_FILE = "royaaa.m3u"

# استثناء القنوات حسب tvg-id أو الاسم
EXCLUDE_IDS = ["1515459"]            # استثناء حسب ID
EXCLUDE_NAMES = ["معلومات عن الخدمة"]  # استثناء حسب الاسم

# إعداد headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

resp = requests.get(URL, headers=HEADERS, timeout=20)
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

    # استثناء القناة إذا كان الـ ID أو الاسم موجود في القوائم
    if ch_id in EXCLUDE_IDS or name in EXCLUDE_NAMES:
        print(f"⚠️ تم استثناء القناة: {name} (ID: {ch_id})")
        continue

    logo_tag = a.select_one(".card-thumbnail img")
    logo = logo_tag["src"] if logo_tag else ""
    channel_url = f"https://v5on.site/{href}"

    channels.append((ch_id, name, logo, channel_url))

if not channels:
    print("⚠️ لم يتم العثور على أي قناة.")
else:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch_id, name, logo, channel_url in channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n')
            f.write(channel_url + "\n")
    print(f"✔ تم حفظ {len(channels)} قناة في {OUTPUT_FILE}")
