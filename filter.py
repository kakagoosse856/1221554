import requests
import os

INPUT_FILE = "s4.m3u"  # ملف القنوات الأصلي
OUTPUT_FILE = "s7.m3u"           # ملف القنوات الحية النهائي

# قراءة القنوات الموجودة مسبقًا (إن وجدت)
existing_channels = set()
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                existing_channels.add(line)

# قائمة القنوات الجديدة الحية
new_alive = set()

try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("❌ ملف all_channels.m3u غير موجود")
    exit(0)

for line in lines:
    url = line.strip()
    if not url or url.startswith("#"):
        continue

    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            new_alive.add(url)
            print("✔ حي:", url)
        else:
            print("✖ ميت:", url)
    except:
        print("✖ خطأ:", url)

# دمج القنوات القديمة والحية الجديدة
merged_alive = existing_channels.union(new_alive)

# كتابة القنوات النهائية في ملف واحد مرتب
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in sorted(merged_alive):
        f.write(ch + "\n")

print(f"✅ تم حفظ {len(merged_alive)} قناة حية في {OUTPUT_FILE}")
