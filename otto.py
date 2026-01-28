import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import time

BASE_URL = "https://v5on.site/"
START_URL = "https://v5on.site/index.php"

os.makedirs("m3u", exist_ok=True)

def clean_name(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

# جلب الصفحة الرئيسية
resp = requests.get(START_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# استخراج كل الباقات
categories = {}
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "cat=" in href:
        name = a.get_text(strip=True)
        if name and len(name) > 2:
            categories[name] = urljoin(BASE_URL, href)

print(f"[+] تم العثور على {len(categories)} باقة")

# معالجة كل باقة
for cat_name, cat_url in categories.items():
    safe_name = clean_name(cat_name)
    output_file = f"m3u/{safe_name}.m3u"

    print(f"[+] استخراج باقة: {cat_name}")

    resp = requests.get(cat_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    channels = []

    for a in soup.find_all("a", href=True):
        href = a.get("href")
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

    print(f"    ✔ {len(channels)} قناة → {output_file}")
    time.sleep(1)

print("\n✅ انتهى استخراج كل الباقات")
print("Auto run finished")
