from playwright.sync_api import sync_playwright
import sys

WATCH_URL = "https://dlhd.dad/watch.php?id=91"
OUTPUT_FILE = "bein.m3u"

def extract_m3u8():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
        page = context.new_page()
        m3u8_links = set()

        def on_request(request):
            url = request.url
            if ".m3u8" in url and "beIN" in url:  # فلترة لقنوات beIN فقط
                m3u8_links.add(url)

        page.on("request", on_request)
        page.goto(WATCH_URL, timeout=60000)
        page.click("button.player-btn.is-active", timeout=15000)
        page.wait_for_timeout(15000)
        browser.close()
        return list(m3u8_links)


if __name__ == "__main__":
    links = extract_m3u8()
    if not links:
        print("[ERROR] لم يتم العثور على أي m3u8")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for l in links:
            f.write(f"#EXTINF:-1,{l.split('/')[-2]}\n")  # اسم القناة من الرابط
            f.write(f"{l}\n")

    print(f"[INFO] Saved {len(links)} links to {OUTPUT_FILE}")
