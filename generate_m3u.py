import requests
from bs4 import BeautifulSoup

# رابط الموقع الأساسي
BASE_URL = "https://v5on.site/"
# رابط صفحة القنوات
PAGE_URL = BASE_URL + "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/v5.html"  # عدله حسب الصفحة الصحيحة

# اسم ملف M3U النهائي
M3U_FILE = "channels.m3u"

# جلب الصفحة
resp = requests.get(PAGE_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# إيجاد جميع القنوات
channels = []
for a in soup.select("a.channel-card"):
    href = a.get("href")
    if not href or "play.php?id=" not in href:
        continue
    channel_id = href.split("id=")[-1]
    name_tag = a.select_one("h4")
    channel_name = name_tag.text.strip() if name_tag else f"Channel {channel_id}"
    channels.append((channel_id, channel_name))

# إنشاء ملف M3U
with open(M3U_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for cid, cname in channels:
        f.write(f"#EXTINF:-1,{cname}\n")
        f.write(f"{BASE_URL}play.php?id={cid}\n\n")

print(f"✅ تم إنشاء {M3U_FILE} بنجاح، عدد القنوات: {len(channels)}")
