import requests
from bs4 import BeautifulSoup

# رابط الموقع الذي يحتوي على القنوات
URL = "https://v5on.site/index.php?cat=1736"

# اسم ملف M3U الناتج
OUTPUT_FILE = "rmc.m3u"

# 🔹 قائمة القنوات المراد استخراجها (فلترة حسب الاسم)
ALLOWED = ["RMC"]

# إرسال طلب للموقع
resp = requests.get(URL)
resp.raise_for_status()

# تحليل الصفحة
soup = BeautifulSoup(resp.text, "html.parser")

# استخراج القنوات
channels = []
for a in soup.select("a.channel-card"):
    href = a.get("href", "")
    if "play.php?id=" not in href:
        continue

    ch_id = href.split("id=")[-1].strip()

    # استخراج اسم القناة
    name_tag = a.select_one(".card-info h4")
    name = name_tag.text.strip() if name_tag else f"Channel {ch_id}"

    # ✅ فلترة القنوات: RMC فقط
    if not any(k in name.lower() for k in ALLOWED):
        continue

    # استخراج شعار القناة
    logo_tag = a.select_one(".card-thumbnail img")
    logo = logo_tag["src"] if logo_tag else ""

    # رابط التشغيل الكامل (صفحة HTML)
    channel_url = f"https://v5on.site/{href}"

    channels.append((ch_id, name, logo, channel_url))

# كتابة ملف M3U
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch_id, name, logo, channel_url in channels:
        f.write(
            f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" '
            f'tvg-logo="{logo}" group-title="RMC",{name}\n'
        )
        f.write(channel_url + "\n")

print(f"✔ تم حفظ {len(channels)} قناة في {OUTPUT_FILE}")
