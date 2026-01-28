import requests
from bs4 import BeautifulSoup
import json
import time

# رابط الباقة
URL = "https://v5on.site/?cat=416"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://v5on.site/",
}

def fetch_html(url, retries=5, delay=10):
    for attempt in range(retries):
        try:
            print(f"[+] محاولة {attempt+1} لتحميل الصفحة...")
            resp = requests.get(url, headers=HEADERS, timeout=60)
            resp.raise_for_status()
            print("[✓] تم التحميل بنجاح")
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[!] فشل التحميل: {e}")
            time.sleep(delay)
    raise SystemExit("❌ فشل بعد عدة محاولات")

def extract_channels(html):
    soup = BeautifulSoup(html, "html.parser")
    channels = {}

    # كل القنوات غالبًا في script أو div حسب v5on.site
    # هنا نموذج عام يبحث عن روابط m3u8 في الصفحة
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".m3u8") or "playlist.m3u8" in href:
            name = link.get_text(strip=True) or href.split("/")[-1].split(".")[0]
            channels[name] = {"file": href}

    if not channels:
        print("[!] لم يتم العثور على أي قناة")
    else:
        print(f"[✓] تم استخراج {len(channels)} قناة")

    return channels

def save_json(data, filename="channels.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] تم حفظ القنوات في {filename}")

def main():
    html = fetch_html(URL)
    channels = extract_channels(html)
    save_json(channels)

if __name__ == "__main__":
    main()
