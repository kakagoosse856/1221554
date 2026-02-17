import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

# قراءة أرقام الباقات من الملف
SELECTED_CATS_FILE = "selected_cats.txt"
OUTPUT_FILE = "all_araaaab.m3u"

# استثناء القنوات حسب tvg-id أو الاسم
EXCLUDE_IDS = ["1515459"]
EXCLUDE_NAMES = ["معلومات عن الخدمة"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

def load_selected_cats():
    """قراءة أرقام الباقات المختارة من الملف"""
    if not os.path.exists(SELECTED_CATS_FILE):
        print(f"⚠️ الملف {SELECTED_CATS_FILE} غير موجود. سيتم إنشاؤه.")
        # إنشاء ملف افتراضي كمثال
        with open(SELECTED_CATS_FILE, "w", encoding="utf-8") as f:
            f.write("# أضف هنا أرقام الباقات التي تريد استخراجها (رقم واحد في كل سطر)\n")
            f.write("2273  # مثال: |AR| ✪ THMANYAH SPORT\n")
        return []
    
    cats = []
    with open(SELECTED_CATS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # تجاهل الأسطر الفارغة والتعليقات
            if line and not line.startswith("#"):
                # استخراج الرقم فقط (أول كلمة في السطر)
                cat_id = line.split()[0].strip()
                if cat_id.isdigit():
                    cats.append(cat_id)
                else:
                    print(f"⚠️ تم تجاهل سطر غير صالح: {line}")
    
    return cats

def extract_channels_from_cat(cat_id):
    """استخراج القنوات من باقة محددة"""
    url = f"https://v5on.site/index.php?cat={cat_id}"
    print(f"🔍 جاري معالجة الباقة {cat_id}...")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ فشل الاتصال بالباقة {cat_id}: {e}")
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    channels = []
    
    for a in soup.select("a.channel-card"):
        href = a.get("href", "")
        if "play.php?id=" not in href:
            continue
        
        ch_id = href.split("id=")[-1].strip()
        name_tag = a.select_one(".card-info h4")
        name = name_tag.text.strip() if name_tag else f"Channel {ch_id}"
        
        # استثناء القناة إذا كان الـ ID أو الاسم موجود في القوائم
        if ch_id in EXCLUDE_IDS or name in EXCLUDE_NAMES:
            print(f"⚠️ تم استثناء القناة: {name} (ID: {ch_id})")
            continue
        
        logo_tag = a.select_one(".card-thumbnail img")
        logo = logo_tag["src"] if logo_tag else ""
        channel_url = urljoin("https://v5on.site/", href)
        
        channels.append((ch_id, name, logo, channel_url))
    
    print(f"✅ تم العثور على {len(channels)} قناة في الباقة {cat_id}")
    return channels

def main():
    # تحميل قائمة الباقات المختارة
    selected_cats = load_selected_cats()
    
    if not selected_cats:
        print("❌ لم يتم العثور على أي باقات مختارة. يرجى إضافتها في ملف selected_cats.txt")
        return
    
    print(f"📋 سيتم معالجة {len(selected_cats)} باقة: {', '.join(selected_cats)}")
    
    # استخراج القنوات من جميع الباقات
    all_channels = []
    for cat_id in selected_cats:
        channels = extract_channels_from_cat(cat_id)
        all_channels.extend(channels)
    
    # إزالة القنوات المكررة (نفس الـ ID)
    unique_channels = {}
    for ch in all_channels:
        ch_id, name, logo, url = ch
        if ch_id not in unique_channels:
            unique_channels[ch_id] = ch
    
    final_channels = list(unique_channels.values())
    
    if not final_channels:
        print("⚠️ لم يتم العثور على أي قناة.")
        return
    
    # كتابة ملف M3U
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch_id, name, logo, channel_url in final_channels:
            f.write(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n')
            f.write(channel_url + "\n")
    
    print(f"✔ تم حفظ {len(final_channels)} قناة في {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
