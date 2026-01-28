# bm3u8.py
import os
import requests
from bs4 import BeautifulSoup

# ----------------------------
# إعدادات عامة
# ----------------------------
BASE_URL = "https://v5on.site"
CATEGORY_URL = f"{BASE_URL}/index.php?cat=8"
CHANNELS_DIR = "channels"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
    "Accept": "application/json,text/html, */*"
}

os.makedirs(CHANNELS_DIR, exist_ok=True)

# ----------------------------
# جلب قائمة القنوات من صفحة التصنيف
# ----------------------------
print("[INFO] Fetching channel list...")
resp = requests.get(CATEGORY_URL, headers=HEADERS, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

channel_links = soup.select("a[href*='play.php?id=']")
channels = []

for link in channel_links:
    title = link.get_text(strip=True)
    href = link['href']
    # استخراج ID القناة
    if "play.php?id=" in href:
        channel_id = href.split("play.php?id=")[1]
        channels.append({"name": title, "id": channel_id})

print(f"[INFO] Found {len(channels)} channels.")

# ----------------------------
# معالجة كل قناة
# ----------------------------
for ch in channels:
    name = ch["name"].replace("/", "-")  # لتجنب مشاكل أسماء الملفات
    channel_file = os.path.join(CHANNELS_DIR, f"{name}.m3u8")
    api_url = f"{BASE_URL}/api/playlist.php?id={ch['id']}"
    
    try:
        resp = requests.get(api_url, headers=HEADERS, timeout=15)
        data = resp.json()
        
        # التأكد من وجود رابط
        if "link" in data:
            m3u8_link = data["link"]
            # حفظ الملف
            with open(channel_file, "w", encoding="utf-8") as f:
                f.write(f"#EXTM3U\n#EXTINF:0,{name}\n{m3u8_link}\n")
            print(f"[OK] Generated {channel_file}")
        else:
            print(f"[WARN] Channel {name} has no 'link' key in JSON")
            
    except Exception as e:
        print(f"[ERROR] Failed channel {name}: {e}")
