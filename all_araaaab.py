import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re

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

# قاموس لتخزين أرقام الباقات وأسمائها من الملف
SELECTED_CATEGORIES = {}

def load_selected_cats_from_html():
    """قراءة أرقام الباقات وأسمائها من ملف HTML"""
    if not os.path.exists(SELECTED_CATS_FILE):
        print(f"⚠️ الملف {SELECTED_CATS_FILE} غير موجود.")
        return False
    
    print(f"📋 جاري قراءة الباقات من الملف {SELECTED_CATS_FILE}...")
    
    with open(SELECTED_CATS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # استخدام BeautifulSoup لتحليل HTML
    soup = BeautifulSoup(content, "html.parser")
    
    # البحث عن جميع روابط الباقات
    for a in soup.select("a.nav-pill"):
        href = a.get("href", "")
        if "?cat=" in href:
            cat_id = href.split("=")[-1].strip()
            # استخراج اسم الباقة وتنظيفه
            cat_name = a.text.strip()
            # إزالة |AR| ✪ والمسافات الزائدة
            cat_name = cat_name.replace("|AR|", "").replace("✪", "").strip()
            # تنظيف المسافات المتعددة
            cat_name = ' '.join(cat_name.split())
            
            SELECTED_CATEGORIES[cat_id] = cat_name
            print(f"  ✅ {cat_id}: {cat_name}")
    
    print(f"📊 تم تحميل {len(SELECTED_CATEGORIES)} باقة من الملف")
    return len(SELECTED_CATEGORIES) > 0

def extract_channels_from_cat(cat_id, cat_name):
    """استخراج القنوات من باقة محددة"""
    print(f"🔍 جاري معالجة الباقة {cat_id}: {cat_name}")
    
    url = f"https://v5on.site/index.php?cat={cat_id}"
    
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
        
        # إضافة اسم الباقة للقناة
        channels.append((ch_id, name, logo, channel_url, cat_name))
    
    print(f"✅ تم العثور على {len(channels)} قناة في الباقة {cat_id}")
    return channels

def main():
    # قراءة الباقات من ملف HTML
    if not load_selected_cats_from_html():
        print("❌ لم يتم العثور على أي باقات في الملف.")
        return
    
    print(f"📋 سيتم معالجة {len(SELECTED_CATEGORIES)} باقة")
    
    # استخراج القنوات من جميع الباقات
    all_channels = []
    for cat_id, cat_name in SELECTED_CATEGORIES.items():
        channels = extract_channels_from_cat(cat_id, cat_name)
        all_channels.extend(channels)
    
    # إزالة القنوات المكررة (نفس الـ ID)
    unique_channels = {}
    for ch in all_channels:
        ch_id, name, logo, url, cat_name = ch
        if ch_id not in unique_channels:
            unique_channels[ch_id] = ch
    
    final_channels = list(unique_channels.values())
    
    if not final_channels:
        print("⚠️ لم يتم العثور على أي قناة.")
        return
    
    # كتابة ملف M3U مع إضافة group-title (اسم الباقة)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch_id, name, logo, channel_url, cat_name in final_channels:
            # إضافة group-title الذي يمثل اسم الباقة
            f.write(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{cat_name}",{name}\n')
            f.write(channel_url + "\n")
    
    print(f"✔ تم حفظ {len(final_channels)} قناة في {OUTPUT_FILE}")
    print(f"📊 تم استخدام {len(set([ch[4] for ch in final_channels]))} باقة مختلفة")

    # عرض إحصائيات لكل باقة
    print("\n📊 إحصائيات الباقات:")
    cat_stats = {}
    for ch in final_channels:
        cat_name = ch[4]
        if cat_name not in cat_stats:
            cat_stats[cat_name] = 0
        cat_stats[cat_name] += 1
    
    for cat_name, count in sorted(cat_stats.items()):
        print(f"  {cat_name}: {count} قناة")

if __name__ == "__main__":
    main()
