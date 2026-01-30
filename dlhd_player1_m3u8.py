from playwright.sync_api import sync_playwright
import sys

WATCH_URL = "https://dlhd.link/watch.php?id=91"
REFERER = "https://dlhd.link/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
OUTPUT_FILE = "dlhd_player1_m3u8.m3u8"


def main():
    m3u8_links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent=UA,
            extra_http_headers={
                "Referer": REFERER
            }
        )

        page = context.new_page()

        def on_response(response):
            url = response.url
            if ".m3u8" in url:
                print("[FOUND]", url)
                m3u8_links.add(url)

        page.on("response", on_response)

        print("[INFO] Open watch page")
        page.goto(WATCH_URL, wait_until="networkidle", timeout=60000)

        # انتظار تحميل iframe واللاعب
        page.wait_for_timeout(10000)

        # الضغط على Player 1 (إن وجد)
        try:
            page.locator("button.player-btn").first.click()
            page.wait_for_timeout(8000)
        except:
            pass

        browser.close()

    if not m3u8_links:
        print("ERROR: لم يتم العثور على أي m3u8", file=sys.stderr)
        sys.exit(1)

    # حفظ النتائج في ملف
    with open(OUTPUT_FILE, "w") as f:
        for link in sorted(m3u8_links):
            f.write(link + "\n")

    print(f"[INFO] Saved {len(m3u8_links)} m3u8 link(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
