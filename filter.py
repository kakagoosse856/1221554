import requests

INPUT_FILE = "SSULTAN.m3u"
OUTPUT_FILE = "KASSSSKASSSK.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://v5on.site/"
}

TIMEOUT = 8

def alive(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        return r.status_code == 200
    except:
        return False

with open(INPUT_FILE, encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

output = ["#EXTM3U\n"]
i = 0

while i < len(lines):
    if lines[i].startswith("#EXTINF"):
        info = lines[i]
        url = lines[i + 1].strip()

        print("Checking:", url)

        if alive(url):
            output.append(info)
            output.append(url + "\n")
            print(" ✔ WORKS")
        else:
            print(" ✖ DEAD")

        i += 2
    else:
        i += 1

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output)

print("Done. Saved channels:", (len(output) - 1) // 2)
