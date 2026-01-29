import requests
import os

# =====================
# أسماء القنوات (يمكن إضافة أي عدد)
# =====================
CHANNEL_NAMES = [
    "beIN Sports",
    "beIN ",
  
]

# =====================
# مصادر M3U
# =====================
M3U_SOURCES = [
    "https://raw.githubusercontent.com/Walid533112/airmax/refs/heads/main/airmax.m3u"
]

# =====================
# ملف الإخراج
# =====================
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_channels.m3u8")

# =====================
# البحث عن كل الروابط
# =====================
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
                if ch.lower() in name.lower():
                    if ch not in found:
                        found[ch] = []
                    # اجمع كل الروابط، لا تتوقف عند أول واحد
                    if i + 1 < len(text):
                        found[ch].append(text[i + 1].strip())
                        print(f"[FOUND] {ch}: {text[i + 1].strip()}")

# =====================
# كتابة ملف M3U النهائي
# =====================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in CHANNEL_NAMES:
        if ch in found:
            for url in found[ch]:
                f.write(f"#EXTINF:-1,{ch}\n")
                f.write(url + "\n")
        else:
            print(f"[MISS] {ch} لم يُعثر عليه")

print(f"[DONE] تم إنشاء الملف: {OUTPUT_FILE}")
