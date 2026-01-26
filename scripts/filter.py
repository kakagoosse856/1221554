import requests

# اسم ملف M3U الأصلي
input_file = "all_channels.m3u"
# اسم ملف الإخراج
output_file = "KASSSSKASSSK.m3u"

alive_channels = []

# قراءة القنوات من الملف
with open(input_file, "r") as f:
    channels = [line.strip() for line in f if line.strip()]

# اختبار القنوات
for url in channels:
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            alive_channels.append(url)
    except:
        continue

# حفظ القنوات الحية
with open(output_file, "w") as f:
    for ch in alive_channels:
        f.write(ch + "\n")

print(f"تم تحديث {len(alive_channels)} قناة حية في {output_file}")

