import requests
import os
import base64
import json
import time

# =====================
# إعدادات GitHub
# =====================
GITHUB_USER = "اسم_المستخدم_هنا"
GITHUB_REPO = "iptv-playlists"
GITHUB_TOKEN = "ضع_هنا_Personal_Access_Token"
BRANCH = "main"

# =====================
# مجلد حفظ الملفات محلياً
# =====================
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_channels.m3u8")

# =====================
# أسماء القنوات فقط
# =====================
CHANNEL_NAMES = [
    "beIN Sports ",
    "beIN ",
    # أضف باقي القنوات هنا
]

# =====================
# مصادر M3U عامة للبحث التلقائي
# =====================
M3U_SOURCES = [
    "https://gist.githubusercontent.com/mohannad-art/1f08bae8819eb6ced114bc5fd9920dac/raw/Bein_sports.m3u",
    "https://raw.githubusercontent.com/GhaniMaxime/iptv/master/sport.m3u",
    "https://raw.githubusercontent.com/majdsassi/Sport-IPTV-FR/main/index.m3u",
]

# =====================
# الوظيفة الرئيسية لتحديث الملف
# =====================
def update_playlist():
    channel_links = {}
    # تحميل جميع المصادر
    for source in M3U_SOURCES:
        try:
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

    # إنشاء الملف النهائي محلياً
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name in CHANNEL_NAMES:
            url = channel_links.get(name)
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

    # رفع الملف إلى GitHub
    with open(OUTPUT_FILE, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/all_channels.m3u8"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # الحصول على sha إذا كان الملف موجود لتحديثه
    resp_sha = requests.get(api_url, headers=headers)
    sha = resp_sha.json()["sha"] if resp_sha.status_code == 200 else None

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

# =====================
# حلقة تحديث تلقائي كل ساعة (يمكن تعديل الفترة)
# =====================
UPDATE_INTERVAL = 3600  # بالثواني (3600 = ساعة)
while True:
    print("\n[INFO] بدء تحديث القائمة...")
    update_playlist()
    print(f"[INFO] الانتظار {UPDATE_INTERVAL} ثانية قبل التحديث التالي...\n")
    time.sleep(UPDATE_INTERVAL)
