import sys
import re
from playwright.sync_api import sync_playwright

if len(sys.argv) < 2:
    print("Usage: python extract_m3u8.py <channel_id>")
    sys.exit(1)

channel_id = sys.argv[1]
url = f"https://dlhd.link/stream/stream-{channel_id}.php"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    content = page.content()
    browser.close()

# استخراج رابط m3u8 من المحتوى
m3u8_match = re.search(r'(https://.*?\.m3u8\?token=.*?)["\']', content)
if m3u8_match:
    print(f"M3U8 URL: {m3u8_match.group(1)}")
else:
    print("No m3u8 link found")
