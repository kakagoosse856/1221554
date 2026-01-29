import requests
import os

# أسماء القنوات فقط
CHANNEL_NAMES = [
    "beIN Sports 1",
    "beIN Sports 2",
    "beIN Sports 3",
]

# مصادر M3U
M3U_SOURCES = [
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/SSULTAN.m3u"
]

OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "beinotto.m3u8")

found = {}

print("[INFO] بدء البحث...")

for src in M3U_SOURCES:
    print(f"[INFO] تحميل المصدر: {src}")
    try:
        text = requests.get(src, timeout=20).text.splitlines()
    except Exception as e:
        print(f"[ERROR] فشل تحميل المصدر: {e}")
        continue

    for i, line in enumerate(text):
        if line.startswith("#EXTINF"):
            name = line.split(",")[-1].strip()
            for ch in CHANNEL_NAMES:
                if ch.lower() in name.lower() and ch not in found:
                    if i + 1 < len(text):
                        found[ch] = text[i + 1].strip()
                        print(f"[FOUND] {ch}")

# إنشاء ملف M3U
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in CHANNEL_NAMES:
        if ch in found:
            f.write(f"#EXTINF:-1,{ch}\n")
            f.write(found[ch] + "\n")
        else:
            print(f"[MISS] {ch} لم يُعثر عليه")

print(f"[DONE] تم إنشاء الملف: {OUTPUT_FILE}")
