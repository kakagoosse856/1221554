import requests

INPUT_FILE = "s4.m3u"
OUTPUT_FILE = "s7.m3u"

alive = []

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
            alive.append(url)
            print("✔ حي:", url)
        else:
            print("✖ ميت:", url)
    except:
        print("✖ خطأ:", url)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in alive:
        f.write(ch + "\n")

print(f"✅ تم حفظ {len(alive)} قناة حية في {OUTPUT_FILE}")
