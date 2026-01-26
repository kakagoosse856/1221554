import requests
import re

BASE_URL = "https://v5on.site/"
PAGE_URL = BASE_URL  # الصفحة الرئيسية
OUTPUT = "channels.m3u"

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("🔍 جلب الصفحة...")
r = requests.get(PAGE_URL, headers=headers, timeout=15)
r.raise_for_status()

html = r.text

# استخراج كل IDs
ids = sorted(set(re.findall(r'play\.php\?id=(\d+)', html)))

print(f"✅ تم العثور على {len(ids)} قناة")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for cid in ids:
        f.write(f"#EXTINF:-1,Channel {cid}\n")
        f.write(f"{BASE_URL}play.php?id={cid}\n\n")

print("📺 تم إنشاء ملف channels.m3u بنجاح")
