import base64
import re
import requests

SOURCE_URL = "https://raw.githubusercontent.com/omnixmain/OMNIX-PLAYLIST-ZONE/refs/heads/main/playlist/omni_v5on.m3u"
OUTPUT_FILE = "output_direct.m3u8"

resp = requests.get(SOURCE_URL, timeout=20)
resp.raise_for_status()

lines = resp.text.splitlines()
out = []

for line in lines:
    if "segment.php?u=" in line:
        m = re.search(r"u=([^&]+)", line)
        if m:
            b64 = m.group(1).replace(" ", "")
            b64 += "=" * (-len(b64) % 4)
            try:
                out.append(base64.b64decode(b64).decode())
            except Exception:
                pass
    else:
        out.append(line)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE")
