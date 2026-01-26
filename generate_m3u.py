import requests

# رابط M3U الجديد
URL = "https://raw.githubusercontent.com/omnixmain/OMNIX-PLAYLIST-ZONE/refs/heads/main/playlist/BEIN.m3u"

# جلب الملف
resp = requests.get(URL)
resp.raise_for_status()
data = resp.text

# تقسيم الأسطر
lines = data.splitlines()
channels = []

# قراءة القنوات
for i, line in enumerate(lines):
    if line.startswith("#EXTINF:"):
        info = line
        url = lines[i + 1] if i + 1 < len(lines) else ""
        
        # استخراج الاسم من tvg-name
        import re
        name_match = re.search(r'tvg-name="([^"]+)"', info)
        logo_match = re.search(r'tvg-logo="([^"]+)"', info)
        name = name_match.group(1) if name_match else "قناة بدون اسم"
        logo = logo_match.group(1) if logo_match else ""
        
        channels.append({
            "name": name,
            "url": url,
            "logo": logo
        })

# توليد M3U جديد
m3u_lines = ["#EXTM3U\n"]
for ch in channels:
    extinf = f'#EXTINF:-1 tvg-id="{ch["name"]}" tvg-name="{ch["name"]}"'
    if ch["logo"]:
        extinf += f' tvg-logo="{ch["logo"]}"'
    extinf += f', {ch["name"]}'
    m3u_lines.append(extinf)
    m3u_lines.append(ch["url"])

# حفظ الملف
with open("BEIN_new.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u_lines))

print(f"تم استخراج {len(channels)} قناة وتوليد BEIN_new.m3u بنجاح!")
