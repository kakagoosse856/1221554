import requests, re, base64

SOURCE_PLAYLIST = "https://raw.githubusercontent.com/omnixmain/OMNIX-PLAYLIST-ZONE/refs/heads/main/playlist/omni_v5on.m3u"
OUTPUT = "output_direct.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://v5on.site/"
}

playlist = requests.get(SOURCE_PLAYLIST, timeout=20).text.splitlines()
out = ["#EXTM3U"]

for line in playlist:
    if "api/playlist.php?id=" in line:
        api_url = line.split("|")[0]

        try:
            m3u8 = requests.get(api_url, headers=HEADERS, timeout=10).text
        except:
            continue

        for l in m3u8.splitlines():
            if "segment.php?u=" in l:
                m = re.search(r"u=([^&]+)", l)
                if not m:
                    continue

                b64 = m.group(1)
                b64 += "=" * (-len(b64) % 4)

                try:
                    ts = base64.b64decode(b64).decode()
                    out.append(ts)
                except:
                    pass

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE ✔")
