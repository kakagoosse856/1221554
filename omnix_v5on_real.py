import requests
from bs4 import BeautifulSoup
import datetime, pytz, os, time, base64, re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://v5on.site"
TARGET_URL = "https://v5on.site?cat=all"
PLAYLIST_FILE = "playlist/omni_v5on_REAL.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://v5on.site/",
}

session = requests.Session()
session.headers.update(HEADERS)

retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


def get_bd_time():
    tz = pytz.timezone("Asia/Dhaka")
    return datetime.datetime.now(tz).strftime("%Y-%m-%d %I:%M %p (BD Time)")


def api_to_real_m3u8(api_url):
    try:
        r = session.get(api_url, timeout=15)
        for line in r.text.splitlines():
            if "segment.php?u=" in line:
                b64 = re.search(r'u=([^&]+)', line).group(1)
                b64 += "=" * (-len(b64) % 4)
                ts = base64.b64decode(b64).decode()
                return ts.rsplit("/", 1)[0] + "/index.m3u8"
    except:
        return None


def fetch_channels():
    soup = BeautifulSoup(session.get(TARGET_URL).text, "html.parser")
    cards = soup.select('a[href*="play.php?id="]')
    channels = []

    for a in cards:
        cid = a["href"].split("id=")[1]
        name = a.get_text(strip=True) or f"Channel {cid}"

        channels.append({
            "id": cid,
            "name": name.replace(",", " "),
            "logo": "",
            "cat": "Live TV",
            "api": f"{BASE_URL}/api/playlist.php?id={cid}"
        })

    return channels


def generate_m3u(channels):
    header = f"""#EXTM3U
# OMNIX EMPIRE
# Updated: {get_bd_time()}
# Channels: {len(channels)}

"""
    out = [header]

    for ch in channels:
        real = api_to_real_m3u8(ch["api"])
        if not real:
            continue

        out.append(
            f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" group-title="{ch["cat"]}",{ch["name"]}'
        )
        out.append(real)

    return "\n".join(out)


def main():
    print("🚀 OMNIX REAL M3U8 GENERATOR")
    ch = fetch_channels()
    os.makedirs(os.path.dirname(PLAYLIST_FILE), exist_ok=True)

    with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
        f.write(generate_m3u(ch))

    print("✅ DONE:", PLAYLIST_FILE)


if __name__ == "__main__":
    main()
