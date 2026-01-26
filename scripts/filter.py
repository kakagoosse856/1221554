import requests

print("SCRIPT STARTED OK")

INPUT_FILE = "SSULTAN.m3u"
OUTPUT_FILE = "KASSSSKASSSK.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://v5on.site/"
}

def alive(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, stream=True)
        return r.status_code == 200
    except Exception as e:
        print("ERROR:", e)
        return False

with open(INPUT_FILE, encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

out = ["#EXTM3U\n"]
i = 0

while i < len(lines):
    if lines[i].startswith("#EXTINF"):
        info = lines[i]
        url = lines[i + 1].strip()
        print("CHECK:", url)
        if alive(url):
            out.append(info)
            out.append(url + "\n")
            print(" OK")
        else:
            print(" DEAD")
        i += 2
    else:
        i += 1

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(out)

print("DONE:", (len(out) - 1) // 2)
