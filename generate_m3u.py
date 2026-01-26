import requests
from bs4 import BeautifulSoup

# رابط HTML على GitHub
URL = "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/v5.html"

# جلب الصفحة
resp = requests.get(URL)
resp.raise_for_status()
html = resp.text

# تحليل الصفحة
soup = BeautifulSoup(html, "html.parser")
channels = []

# البحث عن كل القنوات
for a in soup.select("a.channel-card"):
    link = a.get("href")
    name_tag = a.select_one("h4")
    name = name_tag.get_text(strip=True) if name_tag else "قناة بدون اسم"
    logo_tag = a.select_one("img")
    logo = logo_tag["src"] if logo_tag else ""
    channels.append({
        "name": name,
        "url": link,
        "logo": logo
    })

# توليد ملف M3U
m3u_content = "#EXTM3U\n\n"
for ch in channels:
    m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="Live TV",{ch["name"]}\n'
    m3u_content += f'{ch["url"]}\n\n'

# حفظ الملف
with open("v5.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print(f"{len(channels)} قناة تم استخراجها وحفظها في v5.m3u")
