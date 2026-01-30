import sys
from playwright.sync_api import sync_playwright

BASE_URL = "https://codepcplay.fun/premiumtv/daddyhd.php?id={}"

# لو ما مرّرت ID → جرّب من 1 إلى 200
if len(sys.argv) > 1:
    IDS = [int(sys.argv[1])]
else:
    IDS = range(1, 201)

def extract_m3u8(channel_id):
    url = BASE_URL.format(channel_id)
    found = {"m3u8": None}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def on_response(response):
            if ".m3u8" in response.url:
                found["m3u8"] = response.url

        page.on("response", on_response)

        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(5000)
        except Exception:
            pass

        browser.close()

    return found["m3u8"]

for cid in IDS:
    print(f"[+] Trying ID {cid}")
    m3u8 = extract_m3u8(cid)

    if m3u8:
        print(f"✅ FOUND → ID {cid}")
        print(m3u8)
        break
    else:
        print("❌ Not found")
