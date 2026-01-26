import requests

# قائمة القنوات لاختبار مثال
channels = [
    "http://example.com/stream1.m3u8",
    "http://example.com/stream2.m3u8"
]

alive_channels = []

for url in channels:
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            alive_channels.append(url)
    except:
        continue

# حفظ النتائج في ملف M3U
with open("KASSSSKASSSK.m3u", "w") as f:
    for ch in alive_channels:
        f.write(ch + "\n")

print("تم تحديث القنوات الحية")
