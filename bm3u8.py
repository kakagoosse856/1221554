import requests
from bs4 import BeautifulSoup
import os
import base64

# ---------------- CONFIG ----------------
CATEGORY_URL = "https://v5on.site/index.php?cat=8"  # رابط الصفحة
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://v5on.site/"
}
OUTPUT_DIR = "channels"  # مجلد حفظ ملفات m3u8
TIMEOUT = 20
# ---------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("[INFO] Fetching channel list...")

try:
    resp = requests.get(CATEGORY_URL, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
except Exception as e:
    print("[ERROR] Failed to fetch category page:", e)
    exit(1)

soup = BeautifulSoup(resp.text, 'html.parser')
channels = []

# استخراج كل الروابط play.php?id=XXXX
for a in soup.find_all('a', href=True):
    href = a['href']
    if 'play.php?id=' in href:
        cid = href.split('id=')[1].split('&')[0]
        cname = a.get_text(strip=True)
        if cname:
            channels.append((cid, cname))

print(f"[INFO] Found {len(channels)} channels.")

if not channels:
    exit(0)

# معالجة كل قناة
for cid, cname in channels:
    print(f"[INFO] Processing channel: {cname} (id={cid})")
    try:
        url = f"https://v5on.site/api/playlist.php?id={cid}"
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # بعض الروابط تكون مباشرة m3u8 وبعضها تحتوي segment.php?u=
        # سنحول كل segment.php?u=Base64 إلى رابط ts حقيقي
        if isinstance(data, list):
            ts_links = []
            for item in data:
                link = item.get('link') or item.get('url')  # بعض القنوات
                if not link:
                    continue
                if "segment.php?u=" in link:
                    u_param = link.split("segment.php?u=")[1].split("&")[0]
                    try:
                        decoded = base64.b64decode(u_param).decode()
                        ts_links.append(decoded)
                    except:
                        ts_links.append(link)  # إذا فشل الباس64
                else:
                    ts_links.append(link)
        else:
            ts_links = [url]

        # إنشاء ملف m3u8 باسم القناة
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in cname)
        m3u_file = os.path.join(OUTPUT_DIR, f"{safe_name}.m3u8")

        with open(m3u_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for idx, ts in enumerate(ts_links):
                f.write(f"#EXTINF:10,{safe_name}_{idx}\n{ts}\n")
        print(f"[OK] Generated {m3u_file}")

    except Exception as e:
        print(f"[ERROR] Failed channel {cname}: {e}")

print("[INFO] Done.")
