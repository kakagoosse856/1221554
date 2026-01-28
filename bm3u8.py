import requests
import re
import base64
import os
import time

BASE = "https://v5on.site"
CATEGORY_URL = BASE + "/index.php?cat=2136"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE
}

OUT_DIR = "channels"
os.makedirs(OUT_DIR, exist_ok=True)

def clean_name(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def decode_segment(line):
    m = re.search(r'u=([^&]+)', line)
    if not m:
        return None
    try:
        return base64.b64decode(m.group(1)).decode()
    except:
        return None

print("[INFO] Fetching channel list...")
html = requests.get(CATEGORY_URL, headers=HEADERS, timeout=30).text

channels = re.findall(
    r'play\.php\?id=(\d+).*?title="([^"]+)"',
    html
)

print(f"[INFO] Found {len(channels)} channels.")

for cid, cname in channels:
    cname = clean_name(cname)
    api = f"{BASE}/api/playlist.php?id={cid}"

    try:
        r = requests.get(api, headers=HEADERS, timeout=20)
        r.raise_for_status()
        lines = r.text.splitlines()

        out = []
        for line in lines:
            if line.startswith("#"):
                out.append(line)
            elif "segment.php" in line:
                real = decode_segment(line)
                if real:
                    out.append(real)
            elif line.startswith("http"):
                out.append(line)

        path = f"{OUT_DIR}/{cname}.m3u8"
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")

        print(f"[OK] Generated {path}")
        time.sleep(1)

    except Exception as e:
        print(f"[ERROR] Failed channel {cname}: {e}")
