import requests

SOURCE_URL = "https://dokko1new.dvalna.ru/dokko1/premium91/mono.css"
OUTPUT_FILE = "dlhd_player1_m3u8"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://dokko1new.dvalna.ru/"
}

def main():
    r = requests.get(SOURCE_URL, headers=headers, timeout=15)
    r.raise_for_status()

    content = r.text.strip()

    if "#EXTM3U" not in content:
        raise Exception("الملف ليس M3U8 صالح")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("✔ dlhd_player1_m3u8 تم تحديثه بنجاح")

if __name__ == "__main__":
    main()
