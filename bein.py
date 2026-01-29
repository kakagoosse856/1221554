import requests
import os
import base64
import json
import re

# =====================
# إعدادات GitHub (تأخذ من GitHub Actions)
# =====================
GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BRANCH = "main"

# =====================
# مجلد حفظ الملفات محلياً
# =====================
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_channels.m3u8")

# =====================
# أسماء القنوات (يمكن أن تكون بالعربية)
# =====================
CHANNEL_NAMES = [
    "beIN Sports 1 ",
    "beIN ",
    "beIN Sports 3 ",
    # أضف باقي القنوات هنا
]

# =====================
# مصادر M3U عامة
# =====================
M3U_SOURCES = [
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/SSULTAN.m3u",
    # أضف أي مصدر آخر هنا
]

# =====================
# تحويل اسم القناة لاسم ملف صالح ASCII لتجنب مشاكل الترميز
# =====================
def slugify(name):
    return re.sub(r'[^A-Za-z0-9_\-]', '_', name)

# =====================
# تحميل المصادر وتجميع روابط القنوات
# =====================
channel_links = {}
for source in M3U_SOURCES:
    try:
        print(f"[INFO] تحميل المصدر: {source}")
        resp = requests.get(source, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        lines = resp.text.splitlines()
        current_name = ""
        for line in lines:
            if line.startswith("#EXTINF"):
                current_name = line.split(",")[-1].strip()
            elif line.endswith(".m3u8") and current_name:
                if current_name not in channel_links:
                    channel_links[current_name] = line.strip()
                current_name = ""
    except Exception as e:
        print(f"[WARN] فشل تحميل المصدر: {source} ({e})")

# =====================
# إنشاء ملف M3U واحد للقنوات الصالحة
# =====================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for name in CHANNEL_NAMES:
        url = None
        # بحث جزئي لتجنب مشكلة الاسم المختلف في المصادر
        for key, link in channel_links.items():
            if name.lower() in key.lower():
                url = link
                break
        if url:
            try:
                r = requests.head(url, timeout=10)
                if r.status_code == 200:
                    f.write(f"#EXTINF:-1,{name}\n")
                    f.write(f"{url}\n")
                    print(f"[OK] {name} صالح")
                else:
                    print(f"[SKIP] {name} الرابط غير متاح")
            except requests.RequestException:
                print(f"[SKIP] {name} خطأ في الوصول للرابط")
        else:
            print(f"[NOT FOUND] {name} لم يتم العثور على رابط صالح")

print(f"[DONE] الملف المحلي تم إنشاؤه: {OUTPUT_FILE}")

# =====================
# رفع الملف إلى GitHub
# =====================
with open(OUTPUT_FILE, "rb") as f:
    content = base64.b64encode(f.read()).decode("utf-8")

# يمكن رفع الملف داخل مجلد "channels" داخل المستودع
filename = "channels/all_channels.m3u8"

api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{filename}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

resp_sha = requests.get(api_url, headers=headers)
sha = resp_sha.json().get("sha") if resp_sha.status_code == 200 else None

data = {
    "message": "Auto-update all_channels.m3u8",
    "content": content,
    "branch": BRANCH
}
if sha:
    data["sha"] = sha

resp_put = requests.put(api_url, headers=headers, data=json.dumps(data))
if resp_put.status_code in [200, 201]:
    print("[GITHUB] الملف تم رفعه بنجاح!")
else:
    print(f"[ERROR] فشل رفع الملف: {resp_put.status_code} {resp_put.text}")
