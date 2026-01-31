from playwright.sync_api import sync_playwright

# ضع هنا رابط الصفحة التي تريد استخراج m3u8 منها
url = "https://dlhd.link/watch.php?id=91"

def get_m3u8_links(url):
    m3u8_links = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # False لرؤية المتصفح
        page = browser.new_page()

        # اعتراض كل طلبات الشبكة
        def intercept(route, request):
            if request.url.endswith(".m3u8"):
                m3u8_links.append(request.url)
            route.continue_()

        page.route("**/*", intercept)

        # فتح الصفحة
        page.goto(url)

        # انتظر عدة ثواني حتى يتم تحميل البث
        page.wait_for_timeout(7000)  # 7 ثواني

        browser.close()

    return m3u8_links

# تشغيل الدالة
links = get_m3u8_links(url)

if links:
    print("Found m3u8 links:")
    for l in links:
        print(l)
else:
    print("No m3u8 links found. Try increasing wait time or check the page manually.")
