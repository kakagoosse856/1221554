import requests
import os
from concurrent.futures import ThreadPoolExecutor

INPUT_FILE = "s4.m3u"
OUTPUT_FILE = "s7.m3u"

existing_channels = set()
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                existing_channels.add(line)

new_alive = set()

def check_channel(url):
    if not url or url.startswith("#"):
        return None
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            print("✔ حي:", url)
            return url
        else:
            print("✖ ميت:", url)
    except:
        print("✖ خطأ:", url)
    return None

try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    print("❌ ملف all_channels.m3u غير موجود")
    exit(0)

# فحص القنوات بسرعة باستخدام ThreadPool
with ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(check_channel, urls)

for url in results:
    if url:
        new_alive.add(url)

merged_alive = existing_channels.union(new_alive)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in sorted(merged_alive):
        f.write(ch + "\n")

print(f"✅ تم حفظ {len(merged_alive)} قناة حية في {OUTPUT_FILE}")
