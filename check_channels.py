import requests

# رابط ملف M3U على GitHub أو أي رابط خارجي
M3U_URL = "https://raw.githubusercontent.com/Khz2025/Iptv/refs/heads/main/Supبكور.m3u"

# اسم الملف الجديد للقنوات الشغالة
OUTPUT_FILE = "working_channels.m3u"

def check_channel(url):
    """تحقق من الرابط، يدعم m3u8 و mpd"""
    try:
        # إذا كان رابط DASH (.mpd) نستخدم GET
        if url.endswith(".mpd"):
            r = requests.get(url, timeout=5)
        else:  # m3u8 عادة يدعم HEAD
            r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def main():
    # تحميل الملف
    response = requests.get(M3U_URL)
    lines = response.text.splitlines()

    working_channels = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF:"):
            channel_info = line
            i += 1
            if i < len(lines):
                url = lines[i]
                if check_channel(url):
                    working_channels.append(f"{channel_info}\n{url}")
                    print(f"✅ شغال: {url}")
                else:
                    print(f"❌ لا يعمل: {url}")
        i += 1

    # حفظ النتائج
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("\n".join(working_channels))

    print(f"\nتم الانتهاء! {len(working_channels)} قناة شغالة محفوظة في {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
