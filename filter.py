import requests

# ملف القنوات الأصلي
input_file = "s4.m3u"

# ملف الإخراج للقنوات الحية
output_file = "s7.m3u"

alive_channels = []

# قراءة القنوات من الملف الأصلي
with open(input_file, "r") as f:
    channels = [line.strip() for line in f if line.strip()]

print(f"تم العثور على {len(channels)} قناة في الملف الأصلي.")

# اختبار القنوات
for url in channels:
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            alive_channels.append(url)
            print(f"[✔] قناة حية: {url}")
        else:
            print(f"[✖] قناة غير متاحة: {url}")
    except Exception as e:
        print(f"[✖] خطأ في القناة: {url} ({e})")

# حفظ القنوات الحية في ملف M3U
with open(output_file, "w") as f:
    for ch in alive_channels:
        f.write(ch + "\n")

print(f"تم حفظ {len(alive_channels)} قناة حية في الملف '{output_file}'")
