import re
import sys
from playwright.sync_api import sync_playwright

START_ID = 1
END_ID   = 1200   # عدّل الرقم لو تحب

OUTPUT = "channels.m3u"

def extract_m3u8(page):
    for req in page.context.requests:
        if ".m3u8" in req.url:
            return req.url
    return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )
    page = context.new_page()

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for channel_id in range(START_ID, END_ID + 1):
            url = f"https://dlhd.link/stream/stream-{channel_id}.php"
            print(f"[+] Trying ID {channel_id}")

            try:
                page.goto(url, wait_until="networkidle", timeout=20000)
                m3u8 = extract_m3u8(page)

                if m3u8:
                    print(f"    ✔ FOUND {m3u8}")
                    f.write(f'#EXTINF:-1,DLHD Channel {channel_id}\n')
                    f.write(m3u8 + "\n")
                else:
                    print("    ✖ No m3u8")

            except Exception as e:
                print(f"    ⚠ Error: {e}")

    browser.close()

print(f"\n✅ DONE → saved to {OUTPUT}")
