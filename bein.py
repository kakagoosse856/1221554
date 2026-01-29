import requests
import os
import base64
import json

# =====================
# إعدادات GitHub
# =====================
GITHUB_USER = "اسم_المستخدم_هنا"
GITHUB_REPO = "iptv-playlists"
GITHUB_TOKEN = "ضع_هنا_Personal_Access_Token"
BRANCH = "main"

# =====================
# اسم ملف M3U النهائي
# =====================
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_channels.m3u8")

# =====================
# أسماء القنوات فقط
# =====================
CHANNEL_NAMES = [
    "beIN Sports 1 HD",
    "beIN Sports 2 HD",
    "beIN Sports 3 HD",
    # أضف باقي القنوات هنا
]

# =====================
# مصدر M3U عام
# =====================
M3U_URL = "https://gist.githubusercontent.com/mohannad-art/1f08bae8819eb6ced114bc5fd9920dac/raw/Bein_sports.m3u"

# تحميل قائمة M3U
resp = requests.get(M3U_URL, headers={"User-Agent": "Mozilla/5.0"})
playlist_lines = resp.text.splitlines()

# تحويل M3U إلى قاموس: اسم القناة → الرابط
channel_links = {}
current_name = ""
for line in playlist_lines:
    if line.startswith("#EXTINF"):
        current_name = line.split(",")[-1].strip()
    elif line.endswith(".m3u8") and current_name:
        channel_links[current_name] = line.strip()
        current_name = ""

# =====================
# إنشاء ملف M3U واحد للقنوات الصالحة
# =====================
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

print(f"[DONE] الملف النهائي تم إنشاؤه: {OUTPUT_FILE}")

# =====================
# رفع الملف إلى GitHub
# =====================
with open(OUTPUT_FILE, "rb") as f:
    content = base64.b64encode(f.read()).decode("utf-8")

api_url = f"https://github.com/"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# الحصول على sha إذا كان الملف موجود لتحديثه
resp_sha = requests.get(api_url, headers=headers)
sha = resp_sha.json()["sha"] if resp_sha.status_code == 200 else None

data = {
    "message": "Add/update all_channels.m3u8",
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
