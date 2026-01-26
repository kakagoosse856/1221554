import requests
import re

BASE = "https://v5on.site/"
OUTPUT = "v5on_channels.m3u"

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("📡 جلب الصفحة الرئيسية...")
html = requests.get(BASE, headers=headers, timeout=15).text

# استخراج كل IDs
ids = sorted(set(re.findall(r'play\.php\?id=(\d+)', html)))

print(f"✅ تم استخراج {len(ids)} قناة")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for cid in ids:
        f.write(
            f'#EXTINF:-1 tvg-id="{cid}" group-title="V5ON",Channel {cid}\n'
        )
        f.write(f"{BASE}play.php?id={cid}\n\n")

print("🎉 تم إنشاء ملف M3U بنجاح")
