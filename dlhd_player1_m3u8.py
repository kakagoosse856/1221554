import sys
from playwright.sync_api import sync_playwright

if len(sys.argv) < 2:
    print("Usage: python extractor.py <channel_id>")
    sys.exit(1)

channel_id = sys.argv[1]

STREAM_URL = f"https://dlhd.link/stream/stream-{channel_id}.php"
REFERER = f"https://dlhd.link/watch.php?id={channel_id}"

found = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        extra_http_headers={"Referer": REFERER}
    )

    page = context.new_page()

    def on_request(req):
        url = req.url
        if ".m3u8" in url:
            found.add(url)

    page.on("request", on_request)

    print(f"[+] Loading channel {channel_id}")
    page.goto(STREAM_URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(8000)

    browser.close()

if found:
    print("\n[✔] M3U8 LINKS FOUND:")
    for u in found:
        print(u)
else:
    print("\n[✘] No M3U8 found")
