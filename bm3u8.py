import requests
import time
import os
import json

# قائمة القنوات مع الـ ID الخاص بها
CHANNELS = [
    {"name": "beIN Sports 1 HD", "id": "1"},
    {"name": "beIN Sports 2 HD", "id": "2"},
    # أضف باقي القنوات هنا...
]

# مجلد لحفظ ملفات M3U8
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://v5on.site/",
    "Origin": "https://v5on.site"
}

def fetch_channel(channel):
    url = f"https://v5on.site/api/playlist.php?id={channel['id']}"
    retries = 3
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                print(f"[WARN] {channel['name']} returned status {resp.status_code}")
                time.sleep(2)
                continue
            if not resp.text.strip():
                print(f"[WARN] {channel['name']} فارغة أو محجوبة")
                return None

            data = resp.json()  # تحويل JSON
            return data
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"[ERROR] Attempt {attempt+1} failed for {channel['name']}: {e}")
            time.sleep(2)
    return None

def save_m3u8(channel_name, data):
    filename = os.path.join(OUTPUT_DIR, f"{channel_name}.m3u8")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        f.write("#EXT-X-TARGETDURATION:10\n")
        f.write("#EXT-X-MEDIA-SEQUENCE:0\n")
        for i, item in enumerate(data.get("playlist", [])):
            f.write(f"#EXTINF:10,{channel_name}_{i}\n")
            f.write(f"{item['file']}\n")
        f.write("#EXT-X-ENDLIST\n")
    print(f"[OK] Generated {filename}")

def main():
    print("[INFO] Fetching channel list...")
    for channel in CHANNELS:
        print(f"[INFO] Processing channel: {channel['name']}")
        data = fetch_channel(channel)
        if data:
            save_m3u8(channel['name'], data)

if __name__ == "__main__":
    main()
