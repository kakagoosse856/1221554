import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re

# قراءة أرقام الباقات من الملف
SELECTED_CATS_FILE = "selected_cats.txt"
OUTPUT_FILE = "all_ennnng.m3u"

# استثناء القنوات حسب tvg-id أو الاسم
EXCLUDE_IDS = ["1515459"]
EXCLUDE_NAMES = ["معلومات عن الخدمة"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

# قاموس لتخزين أرقام الباقات وأسمائها
CATEGORIES = {}

def load_categories_from_file():
    """قراءة أرقام الباقات وأسمائها من ملف selected_cats1.txt"""
    if not os.path.exists(SELECTED_CATS_FILE):
        print(f"⚠️ الملف {SELECTED_CATS_FILE} غير موجود.")
        return False
    
    print(f"📋 جاري قراءة الباقات من {SELECTED_CATS_FILE}...")
    
    with open(SELECTED_CATS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # تجاهل الأسطر الفارغة والتعليقات التي تبدأ بـ #
            if not line or line.startswith("#"):
                continue
            
            # تنسيق السطر: رقم_الباقة # اسم_الباقة
            if "#" in line:
                parts = line.split("#", 1)
                cat_id = parts[0].strip()
                cat_name = parts[1].strip()
                
                # تنظيف اسم الباقة
                cat_name = cat_name.replace("|AR|", "").replace("✪", "").strip()
                cat_name = re.sub(r'\s+', ' ', cat_name)  # إزالة المسافات الزائدة
                
                if cat_id.isdigit():
                    CATEGORIES[cat_id] = cat_name
                    print(f"  ✅ {cat_id}: {cat_name}")
    
    print(f"📊 تم تحميل {len(CATEGORIES)} باقة")
    return len(CATEGORIES) > 0

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
        if logo and not logo.startswith("http"):
            logo = urljoin("https://v5on.site/", logo)
        
        channel_url = urljoin("https://v5on.site/", href)
        
        # إضافة القناة مع اسم الباقة
        channels.append({
            'id': ch_id,
            'name': name,
            'logo': logo,
            'url': channel_url,
            'category': cat_name  # اسم الباقة الحقيقي
        })
    
    print(f"✅ تم العثور على {len(channels)} قناة")
    return channels

def main():
    # 1. قراءة الباقات من الملف
    if not load_categories_from_file():
        print("❌ لم يتم العثور على أي باقات في الملف.")
        return
    
    # 2. استخراج القنوات من كل باقة
    all_channels = []
    for cat_id, cat_name in CATEGORIES.items():
        channels = extract_channels_from_cat(cat_id, cat_name)
        all_channels.extend(channels)
    
    # 3. إزالة القنوات المكررة (نفس الـ ID)
    unique_channels = {}
    for ch in all_channels:
        if ch['id'] not in unique_channels:
            unique_channels[ch['id']] = ch
    
    final_channels = list(unique_channels.values())
    
    if not final_channels:
        print("⚠️ لم يتم العثور على أي قناة.")
        return
    
    # 4. كتابة ملف M3U مع اسم الباقة في group-title
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for ch in final_channels:
            # كتابة معلومات القناة مع group-title = اسم الباقة الحقيقي
            f.write(f'#EXTINF:-1 tvg-id="{ch["id"]}" '
                   f'tvg-name="{ch["name"]}" '
                   f'tvg-logo="{ch["logo"]}" '
                   f'group-title="{ch["category"]}",{ch["name"]}\n')
            f.write(ch["url"] + "\n")
    
    print(f"✔ تم حفظ {len(final_channels)} قناة في {OUTPUT_FILE}")
    
    # 5. عرض إحصائيات الباقات
    print("\n📊 إحصائيات الباقات:")
    cat_stats = {}
    for ch in final_channels:
        cat_name = ch['category']
        cat_stats[cat_name] = cat_stats.get(cat_name, 0) + 1
    
    for cat_name, count in sorted(cat_stats.items()):
        print(f"  {cat_name}: {count} قناة")

if __name__ == "__main__":
    main()
