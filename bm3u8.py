import requests
from bs4 import BeautifulSoup
import os
import datetime
import pytz
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===== CONFIGURATION =====
BASE_URL = "https://v5on.site"
TARGET_URL = "https://v5on.site/index.php?cat=2136"
PLAYLIST_DIR = "channels"  # مجلد لحفظ ملفات m3u8
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": BASE_URL
}

# ===== SESSION مع Retry تلقائي =====
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)
session.headers.update(HEADERS)

# ===== HELPER FUNCTIONS =====
def get_bd_time():
    tz = pytz.timezone('Asia/Dhaka')
    return datetime.datetime.now(tz).strftime("%Y-%m-%d %I:%M %p (BD Time)")

def fetch_soup(url):
    try:
        print(f"[INFO] Fetching {url}...")
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch page: {e}")
        return None

def extract_channels(soup):
    channels = []
    if not soup: return channels
    cards = soup.select('a[href*="play.php?id="]')
    for card in cards:
        try:
            href = card['href']
            if 'play.php?id=' not in href: continue
            ch_id = href.split('id=')[1].split('&')[0]
            name = card.get_text(strip=True) or f"Channel_{ch_id}"
            channels.append({
                "id": ch_id,
                "name": name,
                "url": f"{BASE_URL}/api/playlist.php?id={ch_id}"
            })
        except:
            continue
    return channels

def fetch_channel_m3u8(ch):
    """Try fetching channel; retry handled by session"""
    try:
        resp = session.get(ch['url'], timeout=15)
        resp.raise_for_status()
        content = resp.text.strip()
        # إذا كان فارغ أو خطأ
        if not content or "error" in content.lower():
            raise ValueError("Empty or error content")
        return content
    except requests.RequestException as e:
        print(f"[FAILED] قناة {ch['name']} ({ch['id']}) : {e}")
        return None
    except ValueError as ve:
        print(f"[FAILED] قناة {ch['name']} ({ch['id']}) : {ve}")
        return None

def save_m3u8(ch, content):
    os.makedirs(PLAYLIST_DIR, exist_ok=True)
    safe_name = ch['name'].replace('/', '_').replace('\\', '_').replace(' ', '_')
    file_path = os.path.join(PLAYLIST_DIR, f"{safe_name}.m3u8")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] Generated {file_path}")

# ===== MAIN =====
def main():
    print("[INFO] Fetching channel list...")
    soup = fetch_soup(TARGET_URL)
    channels = extract_channels(soup)
    print(f"[INFO] Found {len(channels)} channels.")

    for ch in channels:
        content = fetch_channel_m3u8(ch)
        if content:
            save_m3u8(ch, content)
        time.sleep(1)  # لتخفيف الضغط على السيرفر

if __name__ == "__main__":
    main()
