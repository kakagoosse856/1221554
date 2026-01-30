import requests
from bs4 import BeautifulSoup
import re

WATCH_URL = "https://dlhd.dad/watch.php?id=91"
M3U_PATH = "bein.m3u"

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

M3U8_REGEX = re.compile(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', re.IGNORECASE)

headers = {"User-Agent": DEFAULT_UA}

# 1️⃣ جلب صفحة Watch
resp = requests.get(WATCH_URL, headers=headers, timeout=20)
html = resp.text

# 2️⃣ استخراج رابط Player 1
soup = BeautifulSoup(html, "html.parser")
btn = soup.find("button", {"title": "PLAYER 1"})
player_url = btn.get("data-url") if btn else None

if not player_url:
    # fallback: iframe
    iframe = soup.find("iframe", {"id": "playerFrame"})
    player_url = iframe.get("src") if iframe else None

if not player_url:
    raise RuntimeError("تعذر العثور على رابط Player 1")

print("[INFO] Player URL:", player_url)

# 3️⃣ محاولة البحث عن أي رابط m3u8 في الصفحة
m3u8_links = M3U8_REGEX.findall(html)
print("[DEBUG] m3u8 links found:", m3u8_links)

# 4️⃣ تحديث bein.m3u
if m3u8_links:
    new_url = m3u8_links[0]  # أخذ أول رابط m3u8
    with open(M3U_PATH, "r+", encoding="utf-8") as f:
        lines = f.read().splitlines()
        for i, line in enumerate(lines):
            if "bein sports 1" in line.lower():
                for j in range(i + 1, min(i + 6, len(lines))):
                    if lines[j].startswith("http"):
                        lines[j] = new_url
                        break
                break
        f.seek(0)
        f.write("\n".join(lines) + "\n")
        f.truncate()
    print("[OK] dlhdben1.m3u updated with:", new_url)
else:
    print("[WARN] لم يتم العثور على أي m3u8 في الصفحة.")
