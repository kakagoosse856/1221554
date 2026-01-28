import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import time

BASE_URL = "https://v5on.site/"
START_URL = "https://v5on.site/index.php"

os.makedirs("m3u", exist_ok=True)  # مجلد لحفظ الملفات

def clean_name(name):
    """تنظيف اسم الباقة ليكون صالحًا كاسم ملف"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(headers)

# 1️⃣ جلب الصفحة الرئيسية واستخراج كل روابط الباقات
resp = session.get(START_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

categories = {}
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "cat=" in href:
        name = a.get_text(strip=True)
        if name and len(name) > 2:
            categories[name] = urljoin(BASE_URL, href)

print(f"[+] تم العثور على {len(categories)} باقة")

# 2️⃣ استخراج القنوات لكل باقة وإنشاء ملف M3U
for cat_name, cat_url in categories.items():
    safe_name = clean_name(cat_name)
    output_file = f"m3u/{safe_name}.m3u"
    print(f"[+] معالجة الباقة: {cat_name}")

    resp = session.get(cat_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    channels = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "play.php?id=" not in href:
            continue

        ch_id = href.split("id=")[-1].strip()
        name = a.get_text(strip=True) or f"Channel {ch_id}"
        img = a.find("img")
        logo = img["src"] if img else ""
        channel_url = urljoin(BASE_URL, href)

        channels.append((ch_id, name, logo, channel_url))

    # كتابة ملف M3U للباقة
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch_id, name, logo, channel_url in channels:
            f.write(
                f'#EXTINF:-1 tvg-id="{ch_id}" '
                f'tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'group-title="{cat_name}",{name}\n'
            )
            f.write(channel_url + "\n")

    print(f"    ✔ {len(channels)} قناة محفوظة في {output_file}")
    time.sleep(1)  # لتجنب الحظر

print("\n✅ انتهى استخراج كل الباقات بنجاح")
