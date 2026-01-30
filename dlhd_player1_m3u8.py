from playwright.sync_api import sync_playwright

START_ID = 1
END_ID   = 150   # عدّل العدد براحتك
OUTPUT   = "channels.m3u"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for channel_id in range(START_ID, END_ID + 1):
            print(f"[+] Trying ID {channel_id}")

            page = context.new_page()
            m3u8_url = None

            def catch_request(req):
                nonlocal m3u8_url
                if ".m3u8" in req.url and not m3u8_url:
                    m3u8_url = req.url

            page.on("request", catch_request)

            try:
                page.goto(
                    f"https://dlhd.link/stream/stream-{channel_id}.php",
                    wait_until="networkidle",
                    timeout=20000
                )

                page.wait_for_timeout(5000)

                if m3u8_url:
                    print(f"    ✔ FOUND {m3u8_url}")
                    f.write(f"#EXTINF:-1,DLHD {channel_id}\n")
                    f.write(m3u8_url + "\n")
                else:
                    print("    ✖ No m3u8")

            except Exception as e:
                print(f"    ⚠ Error: {e}")

            page.close()

    browser.close()

print("\n✅ DONE — saved to channels.m3u")
