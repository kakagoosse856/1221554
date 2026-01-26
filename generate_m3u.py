import requests
import re

HTML_URL = "https://raw.githubusercontent.com/kakagoosse856/1221554/main/v5.html"
OUTPUT_M3U = "v5.m3u"
BASE_PLAY_URL = "https://v5on.site/"

resp = requests.get(HTML_URL, timeout=20)
resp.raise_for_status()

html = resp.text

# استخراج كل play.php?id=XXXX
ids = re.findall(r'play\.php\?id=(\d+)', html)

ids = list(dict.fromkeys(ids))  # حذف التكرار

print(f"تم استخراج {len(ids)} قناة")

with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for i, cid in enumerate(ids, 1):
        f.write(f"#EXTINF:-1,Channel {i}\n")
        f.write(f"{BASE_PLAY_URL}play.php?id={cid}\n")

print("✔ تم إنشاء ملف v5.m3u بنجاح")
