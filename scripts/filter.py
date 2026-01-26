import requests

INPUT = "s4.m3u"
OUTPUT = "KASSSSKASSSK.m3u"

with open(INPUT, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

alive = ["#EXTM3U\n"]

for i in range(len(lines)):
    if lines[i].startswith("#EXTINF"):
        url = lines[i+1].strip()

        try:
            r = requests.head(url, timeout=8, allow_redirects=True)
            if r.status_code in [200, 301, 302]:
                alive.append(lines[i])
                alive.append(lines[i+1])
        except:
            pass

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.writelines(alive)

print("DONE → Saved", OUTPUT)
