import os
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://v5on.site/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Referer": "https://v5on.site/"
}

OUTPUT_DIR = "m3u"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(name):
    # إزالة الرموز غير المسموح بها في أسماء الملفات
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name.strip())

def get_bundles():
    """استخراج كل الباقات من الصفحة الرئيسية"""
    print("[+] تحميل الصفحة الرئيسية...")
    resp = requests.get(BASE_URL, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    bundles = []
    for a in soup.select("a.nav-pill"):
        href = a.get("href", "")
        if "?cat=" in href:
            cat_id = href.split("cat=")[-1].strip()
            name = a.text.strip()
            bundles.append((name, cat_id))
    print(f"[+] تم العثور على {len(bundles)} باقة")
    return bundles

def get_channels(cat_id):
    """استخراج كل القنوات داخل باقة معينة"""
    url = f"{BASE_URL}?cat={cat_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    channels = []
    for a in soup.select("a.channel-card"):
        href = a.get("href", "")
        if "play.php?id=" not in href:
            continue
        ch_id = href.split("id=")[-1].strip()
        name_tag = a.select_one(".card-info h4")
        name = name_tag.text.strip() if name_tag else f"Channel_{ch_id}"
        logo_tag = a.select_one(".card-thumbnail img")
        logo = logo_tag["src"] if logo_tag else ""
        # رابط التشغيل الفعلي للقناة
        channel_url = f"{BASE_URL}{href}"
        channels.append((ch_id, name, logo, channel_url))
    return channels

def get_m3u_link(channel_page_url):
    """استخراج رابط M3U8 من صفحة القناة"""
    try:
        resp = requests.get(channel_page_url, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # غالبًا يوجد سكربت JS يحتوي على الرابط النهائي
        script_tags = soup.find_all("script")
        for script in script_tags:
            if "m3u8" in script.text:
                text = script.text
                start = text.find("https://")
                end = text.find(".m3u8") + 5
                if start != -1 and end != -1:
                    return text[start:end]
    except Exception as e:
        print(f"[-] خطأ في استخراج رابط M3U8: {e}")
    return None

def save_m3u(bundle_name, channels):
    """إنشاء ملف M3U لكل باقة"""
    filename = os.path.join(OUTPUT_DIR, sanitize_filename(bundle_name) + ".m3u")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch_id, name, logo, link in channels:
            if link:
                f.write(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n')
                f.write(link + "\n")
    print(f"    ✔ {len(channels)} قناة محفوظة في {filename}")

def main():
    bundles = get_bundles()
    for bundle_name, cat_id in bundles:
        print(f"[+] استخراج باقة: {bundle_name} (cat={cat_id})")
        channels = get_channels(cat_id)
        # تحديث روابط التشغيل لكل قناة
        for i, (ch_id, name, logo, page_url) in enumerate(channels):
            link = get_m3u_link(page_url)
            channels[i] = (ch_id, name, logo, link)
            time.sleep(0.2)  # تقليل الضغط على السيرفر
        save_m3u(bundle_name, channels)

if __name__ == "__main__":
    main()
