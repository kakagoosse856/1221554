import requests
import time

url = "https://v5on.site/?cat=416"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://v5on.site/",
}

for attempt in range(5):
    try:
        print(f"[+] محاولة {attempt+1}")
        resp = requests.get(url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        print("[✓] تم التحميل بنجاح")
        html = resp.text
        break
    except requests.exceptions.RequestException as e:
        print(f"[!] فشل: {e}")
        time.sleep(10)
else:
    raise SystemExit("❌ فشل بعد عدة محاولات")
