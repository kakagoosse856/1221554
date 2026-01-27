import requests
import re

# رابط المصدر
SOURCE_M3U = "https://raw.githubusercontent.com/omnixmain/OMNIX-PLAYLIST-ZONE/refs/heads/main/playlist/BEIN.m3u"
OUTPUT_M3U = "v5.m3u"

resp = requests.get(SOURCE_M3U, timeout=30)
resp.raise_for_status()

lines = resp.text.splitlines()
out = ["#EXTM3U"]

for i in range(len(lines)):
    line = lines[i].strip()
    if line.startswith("#EXTINF"):
        # استخراج الاسم
        name_match = re.search(r'tvg-name="([^"]+)"', line)
        name = name_match.group(1) if name_match else (line.split(',', 1)[1].strip() if ',' in line else "Unknown")
        
        # استخراج ID
        if i + 1 < len(lines):
            url_line = lines[i + 1].strip()
            id_match = re.search(r'id=(\d+)', url_line)
            if not id_match:
                id_match = re.search(r'(\d+)', url_line)
                if not id_match:
                    continue
            cid = id_match.group(1)

            # توليد M3U
            out.append(f'#EXTINF:-1 tvg-id="{cid}",{name}')
            out.append(f'https://v5on.site/play.php?id={cid}')

# حفظ الملف الجديد
with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("✅ v5.m3u تم توليده بنجاح")
