import requests
from bs4 import BeautifulSoup

URL = "https://v5on.site/index.php"

# 🔽 تقسيم الباقات (اسم الملف : كلمات المطابقة)
GROUPS = {
    "rmc.m3u": ["rmc"],
    "canal.m3u": ["canal"]
}

resp = requests.get(URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# إنشاء حاويات لكل ملف
results = {fname: [] for fname in GROUPS}

for a in soup.select("a.channel-card"):
    href = a.get("href", "")
    if "play.php?id=" not in href:
        continue

    ch_id = href.split("id=")[-1].strip()

    name_tag = a.select_one(".card-info h4")
    name = name_tag.text.strip() if name_tag else f"Channel {ch_id}"
    lname = name.lower()

    logo_tag = a.select_one(".card-thumbnail img")
    logo = logo_tag["src"] if logo_tag else ""

    channel_url = f"https://v5on.site/{href}"

    # 🔽 تحديد الملف المناسب
    for filename, keywords in GROUPS.items():
        if any(k in lname for k in keywords):
            results[filename].append((ch_id, name, logo, channel_url))
            break

# كتابة الملفات
for filename, channels in results.items():
    if not channels:
        continue

    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch_id, name, logo, channel_url in channels:
            f.write(
                f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" '
                f'tvg-logo="{logo}" group-title="{filename.replace(".m3u","").upper()}",{name}\n'
            )
            f.write(channel_url + "\n")

    print(f"✔ {filename} : {len(channels)} قناة")
