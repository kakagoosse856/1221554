import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import time

BASE_URL = "https://v5on.site/"
START_URL = "https://v5on.site/index.php"
OUTPUT_DIR = "m3u"  # مجلد حفظ الملفات

os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(headers)

def clean_name(name):
    """تنظيف اسم الباقة ليكون صالحًا كاسم ملف"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

print("[+] تحميل الصفحة الرئيسية...")
resp = session.get(START_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# 1️⃣ استخراج كل الباقات (cat + الاسم)
categories = {}
for a in soup.find_all("a", href=True, class_="nav-pill"):
    href = a["href"]
    if "cat=" in href:
        cat_id = href.split("cat=")[-1].strip()
        cat_name = a.get_text(strip=True)  # النص داخل <a>
        if cat_name:
            categories[cat_id] = cat_name

print(f"[+] تم العثور على {len(categories)} باقة")

# 2️⃣ استخراج القنوات لكل باقة وإنشاء ملف M3U
for cat_id, cat_name in categories.items():
    safe_name = clean_name(cat_name)
    output_file = os.path.join(OUTPUT_DIR, f"{safe_name}.m3u")
    cat_url = urljoin(BASE_URL, f"index.php?cat={cat_id}")
    print(f"[+] استخراج باقة: {cat_name} (cat={cat_id})")

    resp = session.get(cat_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    channels = []

    # استخراج كل القنوات داخل الباقة
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
    time.sleep(1)

print("\n✅ انتهى استخراج كل الباقات بنجاح")
