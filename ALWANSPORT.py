import requests
from bs4 import BeautifulSoup

# رابط صفحة الباقة
URL = "https://v5on.site/index.php?cat=579"

# اسم الملف الناتج
OUTPUT_FILE = "ALWANSPORT.m3u"

# الكلمات المفتاحية للقنوات المراد جلبها
ALLOWED = ["alwan sport"]

# ترويسة لتجنب حظر الموقع
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

try:
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
except Exception as e:
    print(f"❌ خطأ عند الوصول للموقع: {e}")
    exit(1)

soup = BeautifulSoup(resp.text, "html.parser")

channels = []
for a in soup.select("a.channel-card"):
    href = a.get("href", "")
    if "play.php?id=" not in href:
        continue

    ch_id = href.split("id=")[-1].strip()
    name_tag = a.select_one(".card-info h4")
    name = name_tag.text.strip() if name_tag else f"Channel {ch_id}"

    print("Found channel:", name)

    # فلترة حسب الكلمة المفتاحية
    if not any(k in name.lower() for k in ALLOWED):
        continue

    logo_tag = a.select_one(".card-thumbnail img")
    logo = logo_tag["src"] if logo_tag else ""
    channel_url = f"https://v5on.site/{href}"

    channels.append((ch_id, name, logo, channel_url))

if not channels:
    print("⚠️ لم يتم العثور على أي قناة مطابقة. الملف لن يتم إنشاؤه.")
    exit(0)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch_id, name, logo, channel_url in channels:
        f.write(
            f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" '
            f'tvg-logo="{logo}" group-title="ALWANSPORT",{name}\n'
        )
        f.write(channel_url + "\n")

print(f"✔ تم حفظ {len(channels)} قناة في {OUTPUT_FILE}")
