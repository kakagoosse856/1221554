from playwright.sync_api import sync_playwright
import re

TARGET_URL = "https://dlhd.link/watch.php?id=91"
REFERER = "https://dlhd.link/"

def extract_m3u8():
    found = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": REFERER
            }
        )

        page = context.new_page()

        def on_response(response):
            url = response.url
            if ".m3u8" in url:
                found.add(url)
                print("[M3U8 FOUND]", url)

        page.on("response", on_response)

        print("[*] Opening page...")
        page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)

        # انتظر تحميل iframe
        page.wait_for_timeout(10000)

        # جرب الضغط على جميع Players
        buttons = page.locator(".player-btn")
        count = buttons.count()

        print(f"[*] Players detected: {count}")

        for i in range(count):
            try:
                buttons.nth(i).click()
                page.wait_for_timeout(5000)
            except:
                pass

        browser.close()

    return found


if __name__ == "__main__":
    links = extract_m3u8()

    if not links:
        print("❌ لم يتم العثور على أي m3u8")
        exit(1)

    print("\n✅ روابط m3u8 النهائية:")
    for l in links:
        print(l)
