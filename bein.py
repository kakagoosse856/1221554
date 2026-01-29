import requests
import os

SOURCES = [
    "https://raw.githubusercontent.com/a7shk1/m3u-broadcast/bddbb1a1a24b50ee3e269c49eae50bef5d63894b/bein.m3u",
    "https://raw.githubusercontent.com/Yusufdkci/iptv/71fabe363ebf0c3d46ae0ce69f8e3202164b7edc/liste.m3u",
     "https://raw.githubusercontent.com/azzaroflex-star/Xpola-player/refs/heads/main/Bin.tst.m3u"
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
            print(f"[ERROR] {e}")
            continue

        for i, line in enumerate(lines):
            if not line.startswith("#EXTINF") or i + 1 >= len(lines):
                continue

            # يبحث فقط عن BEIN
            if "BEIN" not in line.upper():
                continue

            # 🚫 استثناء أي قناة فيها ⚽️
            if "كيف احصل على الكود" in line:
                continue

            url = lines[i + 1].strip()

            # تحقق من أن الرابط حي
            try:
                r = requests.get(url, timeout=6, stream=True)
                if r.status_code != 200:
                    continue
            except:
                continue

            f.write(line + "\n")
            f.write(url + "\n")
            channels_found += 1
            print(f"[OK] {line}")

print(f"[DONE] تم استخراج {channels_found} قناة BEIN بدون ⚽️")
