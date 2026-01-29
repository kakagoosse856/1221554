import requests
import os

# =====================
# أسماء القنوات الحقيقية
# =====================
CHANNEL_NAMES = [
    "beIN Sports 1 HD",
    "beIN Sports 2 HD",
    "beIN Sports 3 HD",
    "beIN Sports 4 HD",
]

# =====================
# مصادر M3U
# =====================
M3U_SOURCES = [
    "https://raw.githubusercontent.com/Walid533112/airmax/refs/heads/main/airmax.m3u",
    "https://raw.githubusercontent.com/Yusufdkci/iptv/71fabe363ebf0c3d46ae0ce69f8e3202164b7edc/liste.m3u"
]

# =====================
# إعدادات الملف
# =====================
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "beinouto.m3u8")

# =====================
# جمع الروابط الصالحة مع إزالة التكرار
# =====================
found = {ch: set() for ch in CHANNEL_NAMES}

print("[INFO] بدء البحث والتحقق من الروابط...")

for src in M3U_SOURCES:
    print(f"[INFO] تحميل المصدر: {src}")
    try:
        lines = requests.get(src, timeout=20).text.splitlines()
    except Exception as e:
        print(f"[ERROR] فشل تحميل المصدر: {e}")
        continue

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            name = line.split(",")[-1].strip()
            url = lines[i + 1].strip() if i + 1 < len(lines) else None
            if not url:
                continue

            for ch in CHANNEL_NAMES:
                if ch.lower() in name.lower():
                    try:
                        resp = requests.head(url, timeout=5, allow_redirects=True)
                        if resp.status_code == 200:
                            found[ch].add(url)
                            print(f"[OK] {ch}: {url}")
                        else:
                            print(f"[SKIP] {ch} رابط غير متاح: {url}")
                    except:
                        print(f"[SKIP] {ch} خطأ بالتحقق من الرابط: {url}")

# =====================
# إنشاء ملف M3U النهائي
# =====================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for ch in CHANNEL_NAMES:
        if found[ch]:
            for url in sorted(found[ch]):
                f.write(f"#EXTINF:-1,{ch}\n")
                f.write(url + "\n")
        else:
            print(f"[MISS] {ch} لم يُعثر على روابط صالحة")

print(f"[DONE] تم إنشاء الملف النهائي: {OUTPUT_FILE}")
