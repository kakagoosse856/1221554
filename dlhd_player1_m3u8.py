BASE_URL = "https://YOURDOMAIN/stream"
CHANNEL_ID = 91
OUTPUT = "channels.m3u"

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    for p in range(1, 6):
        f.write(f"#EXTINF:-1,BEIN SPORTS 1 | Player {p}\n")
        f.write("#EXTVLCOPT:http-referrer=https://dlhd.link/\n")
        f.write("#EXTVLCOPT:http-user-agent=Mozilla/5.0\n")
        f.write(f"{BASE_URL}?id={CHANNEL_ID}&player={p}\n\n")

print("channels.m3u created")
