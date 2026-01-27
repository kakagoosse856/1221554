import requests
import os
import datetime
import pytz

# مجلد حفظ الملفات
OUTPUT_DIR = "playlist"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# المصادر
SOURCES = [
    ("Armenia", "https://sportsbd.top/playlist/playlist.m3u?id=a1a89c360e48"),
    ("Azerbaijan", "https://sportsbd.top/playlist/playlist.m3u?id=88b1c3bd791e"),
    ("Bangladesh", "https://sportsbd.top/playlist/playlist.m3u?id=a82b3259436a"),
    # أضف باقي المصادر هنا
]

# ترويسة طلبات HTTP
HEADERS = {
    "User-Agent": "VLC/3.0.18 LibVLC/3.0.18",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

def get_bd_time():
    bd_tz = pytz.timezone("Asia/Dhaka")
    now = datetime.datetime.now(bd_tz)
    return now.strftime("%Y-%m-%d %I:%M %p")

def fetch_playlist(name, url):
    try:
        print(f"Fetching {name}...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        content = response.text
        if "#EXTM3U" in content:
            start_index = content.find("#EXTM3U")
            return content[start_index:]
        print(f"Warning: {name} returned content without #EXTM3U marker.")
        return None
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return None

def process_playlist(name, content):
    lines = content.splitlines()
    channel_count = sum(1 for line in lines if line.startswith("#EXTINF"))
    bd_time = get_bd_time()
    header = f"""#EXTM3U
#=================================
# Developed By: OMNIX EMPIER
# IPTV Telegram Channels: https://t.me/omnix_Empire
# Last Updated: {bd_time} (BD Time)
# TV channel counts :- {channel_count}
#==================================
"""
    cleaned_lines = [line for line in lines if line.strip() != "#EXTM3U"]
    return header + "\n".join(cleaned_lines)

def main():
    for name, url in SOURCES:
        slug_name = name.replace(" ", "_")
        filename = f"b1otto-{slug_name}.m3u"
        filepath = os.path.join(OUTPUT_DIR, filename)
        content = fetch_playlist(name, url)
        if content:
            final_content = process_playlist(name, content)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(final_content)
            print(f"Saved {filename}")
        else:
            print(f"Skipping {name}")

if __name__ == "__main__":
    main()
