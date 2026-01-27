import requests
from bs4 import BeautifulSoup

# رابط الموقع الذي يحتوي على القنوات
URL = "https://v5on.site/index.php?cat=29"

# اسم ملف M3U الناتج
OUTPUT_FILE = "frv5on.m3u"

# كلمات مفتاحية للحظر (سيتم حظر أي قناة يحتوي اسمها أو tvg-id على أي كلمة هنا)
BLOCKED_KEYWORDS = [
    "INFORMATIONS",   # مثال على اسم قناة
    "1515460",        # مثال على tvg-id
    "INFORMATIONS SUR LE SERVICE",            # أي قناة تحتوي ADS في الاسم أو ID
]

resp = requests.get(URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# استخراج كل القنوات
channels = []
for a in soup.select("a.channel-card"):
    href = a.get("href")
    if "play.php?id=" not in href:
        continue
    ch_id = href.split("id=")[-1].strip()
    name_tag = a.select_one(".card-info h4")
    name = name_tag.text.strip() if name_tag else f"Channel {ch_id}"
    logo_tag = a.select_one(".card-thumbnail img")
    logo = logo_tag["src"] if logo_tag else ""
    
    # استخراج الرابط الكامل
    channel_url = f"https://v5on.site/{href}"

    # التحقق مما إذا كانت القناة تحتوي على أي كلمة مفتاحية للحظر
    if any(keyword.lower() in name.lower() or keyword in ch_id for keyword in BLOCKED_KEYWORDS):
        print(f"تم حظر القناة: {name} ({ch_id})")
        continue

    channels.append((ch_id, name, logo, channel_url))

# كتابة ملف M3U
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch_id, name, logo, channel_url in channels:
        line1 = f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n'
        line2 = f'{channel_url}\n'
        f.write(line1)
        f.write(line2)

print(f"{len(channels)} قناة مكتوبة في {OUTPUT_FILE}")
