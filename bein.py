import requests
import os

# مصدر القنوات
SOURCES = [
     "https://raw.githubusercontent.com/Walid533112/airmax/refs/heads/main/airmax.m3u",
    "https://raw.githubusercontent.com/Yusufdkci/iptv/71fabe363ebf0c3d46ae0ce69f8e3202164b7edc/liste.m3u"
]

OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bein_auto.m3u8")

channels_found = 0

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

    for src in SOURCES:
        try:
            lines = requests.get(src, timeout=20).text.splitlines()
        except Exception as e:
            print(f"[ERROR] لم أستطع تحميل المصدر {src}: {e}")
            continue

        for i, line in enumerate(lines):
            if line.startswith("#EXTINF") and "BEIN" in line.upper() and i + 1 < len(lines):
                url = lines[i + 1].strip()

                # تحقق من أن الرابط حي
                try:
                    r = requests.get(url, timeout=6, stream=True)
                    if r.status_code != 200:
                        continue
                except:
                    continue

                f.write(f"{line}\n")
                f.write(f"{url}\n")
                channels_found += 1
                print(f"[OK] {line} | {url}")

print(f"[DONE] تم استخراج {channels_found} قناة BEIN في {OUTPUT_FILE}")
