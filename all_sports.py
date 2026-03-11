# sports_channels.py
import requests
import os
import re
import time
from collections import defaultdict

# =====================
# مصادر القنوات
# =====================
SOURCES = [
    {"name": "🇸 🇸 المصدر الأول - SER1", "url": "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser1.m3u"},
    {"name": "🇸 🇸 المصدر الثاني - SER6", "url": "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser6.m3u"},
    {"name": "🇸 🇸 المصدر الثالث - SERV4", "url": "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv4.m3u"},
    {"name": "🇸 🇸 المصدر الرابع - SERV5", "url": "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv5.m3u8"},
    {"name": "🇸 🇸 المصدر الخامس - SERV8", "url": "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv8.m3u8"},
    {"name": "🇸 🇸 المصدر السادس - XTREM2", "url": "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/xtrem2.m3u8"},
    {"name": "🇸 🇸 المصدر السابع - XXTERRM", "url": "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/xxterrm.m3u"},
]

# =====================
# تصنيف القنوات الرياضية
# =====================
SPORTS_PACKAGES = {
    # الباقات العربية
    "بي إن سبورت": {"keywords": ["beIN", "beIN", "البي ان", "بي إن", "bein", "be in", "beIN SPORTS"], "logo": "🇶🇦"},
    "SSC": {"keywords": ["SSC", "ssc", "السعودية", "السعوديه", "SSC1", "SSC2", "SSC3", "SSC4", "SSC5"], "logo": "🇸🇦"},
    "أبوظبي الرياضية": {"keywords": ["AD Sports", "أبوظبي", "abu dhabi", "AD SPORTS", "ABU DHABI"], "logo": "🇦🇪"},
    "الكأس": {"keywords": ["Alkass", "الكأس", "alkass", "AL KASS", "ALKASS"], "logo": "🇶🇦"},
    "أون تايم سبورت": {"keywords": ["ON Time", "أون تايم", "ontime", "ON TIME", "ONTime"], "logo": "🇪🇬"},
    "العراقية الرياضية": {"keywords": ["Iraq", "العراقية", "IRAQ", "العراقيه"], "logo": "🇮🇶"},
    
    # الباقات العالمية
    "Sky Sports": {"keywords": ["Sky Sports", "sky sports", "SKY", "SKY SPORTS"], "logo": "🇬🇧"},
    "BT Sport": {"keywords": ["BT Sport", "bt sport", "BT"], "logo": "🇬🇧"},
    "DAZN": {"keywords": ["DAZN", "dazn", "DAZN1", "DAZN2"], "logo": "🌍"},
    "ESPN": {"keywords": ["ESPN", "espn"], "logo": "🇺🇸"},
    "Eurosport": {"keywords": ["Eurosport", "eurosport"], "logo": "🇪🇺"},
}

OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_sports_sources.m3u8")

def identify_package(text):
    """تحديد الباقة الرياضية"""
    text = text.lower()
    for package, info in SPORTS_PACKAGES.items():
        for keyword in info["keywords"]:
            if keyword.lower() in text:
                return package, info["logo"]
    return "رياضية عامة", "⚽"

print("🚀 بدء استخراج القنوات الرياضية من جميع المصادر...")
print("="*60)

# هيكل البيانات: [المصدر] -> [الباقة] -> [القناة] -> [الروابط]
all_channels = []
total_channels = 0

for source_idx, source in enumerate(SOURCES, 1):
    print(f"\n📡 جاري معالجة {source['name']}...")
    print("-"*40)
    
    try:
        r = requests.get(source['url'], timeout=20)
        lines = r.text.splitlines()
        print(f"✅ تم التحميل - {len(lines)} سطر")
    except Exception as e:
        print(f"❌ فشل تحميل {source['name']}: {str(e)}")
        continue
    
    # تنظيم قنوات هذا المصدر حسب الباقات
    source_channels = defaultdict(lambda: defaultdict(set))
    source_count = 0
    
    for i, line in enumerate(lines):
        if not line.startswith("#EXTINF") or i+1 >= len(lines):
            continue
        
        url = lines[i+1].strip()
        if not (url.endswith(".m3u8") or ".m3u8" in url):
            continue
        
        # استخراج الاسم
        name_match = re.search(r'#EXTINF:-?[0-9]*.*?,(.*)', line)
        if name_match:
            name = name_match.group(1).strip()
        else:
            continue
        
        # تنظيف الاسم
        name = re.sub(r'[^\w\s\u0600-\u06FF:]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        if not name or len(name) < 3:
            continue
        
        # تحديد الباقة
        package, logo = identify_package(name + " " + url)
        
        # حفظ القناة في هذا المصدر
        source_channels[package][name].add(url)
        source_count += 1
        
        # عرض تقدم بسيط
        if source_count % 20 == 0:
            print(f"  ⏳ تم العثور على {source_count} قناة...", end="\r")
    
    # إضافة قنوات هذا المصدر إلى القائمة الرئيسية مع معلومات المصدر
    all_channels.append({
        "source_name": source['name'],
        "source_index": source_idx,
        "channels": source_channels
    })
    
    print(f"  ✅ المصدر {source_idx}: {source_count} قناة رياضية")

print("\n" + "="*60)
print("📝 إنشاء ملف M3U النهائي مرتب حسب المصادر...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write('#EXTINF:-1 tvg-logo="" group-title="معلومات",⚽ جميع القنوات الرياضية مرتبة حسب المصادر\n')
    f.write("# https://t.me/yourchannel\n\n")
    
    total_all = 0
    
    # كتابة القنوات مرتبة حسب المصدر
    for source_data in all_channels:
        source_name = source_data["source_name"]
        source_channels = source_data["channels"]
        
        # إضافة عنوان المصدر كمجموعة
        f.write(f'\n#EXTINF:-1 group-title="📡 المصادر",📡 {source_name}\n')
        f.write('#EXTINF:-1 group-title="المصادر",─────────────────────\n\n')
        
        source_total = 0
        
        # ترتيب الباقات أبجدياً
        for package in sorted(source_channels.keys()):
            logo = SPORTS_PACKAGES.get(package, {}).get("logo", "⚽")
            
            # كتابة عنوان الباقة
            f.write(f'#EXTINF:-1 group-title="{logo} {package}",▶️ {logo} {package}\n')
            
            package_count = 0
            # ترتيب القنوات أبجدياً
            for name in sorted(source_channels[package].keys()):
                urls = list(source_channels[package][name])
                if urls:
                    # اختيار أفضل رابط (أول رابط)
                    best_url = urls[0]
                    f.write(f'#EXTINF:-1 group-title="{logo} {package}" tvg-logo="" ,{name}\n')
                    f.write(f'{best_url}\n')
                    package_count += 1
                    source_total += 1
                    total_all += 1
            
            if package_count > 0:
                f.write(f'#EXTINF:-1 group-title="{logo} {package}",📊 إجمالي {package_count} قناة\n\n')
        
        f.write(f'#EXTINF:-1 group-title="📊 إحصائيات",📊 إجمالي المصدر: {source_total} قناة\n')
        f.write("#EXTINF:-1 group-title=\"إحصائيات\",─────────────────────\n\n")
        
        print(f"  📊 {source_name}: {source_total} قناة")
    
    # إحصائيات نهائية
    f.write("\n#EXTINF:-1 group-title=\"📊 إحصائيات\",═════════════════════════\n")
    f.write(f'#EXTINF:-1 group-title="📊 إحصائيات",🎯 إجمالي القنوات: {total_all} قناة\n')
    f.write('#EXTINF:-1 group-title="📊 إحصائيات",📅 تاريخ التحديث: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')

print("\n" + "="*60)
print(f"✅ تم الانتهاء بنجاح!")
print(f"📁 الملف الناتج: {OUTPUT_FILE}")
print(f"📊 إجمالي القنوات: {total_all} قناة من {len(all_channels)} مصادر")
print("="*60)

# عرض توزيع القنوات
print("\n📊 توزيع القنوات حسب المصادر:")
for i, source_data in enumerate(all_channels, 1):
    source_total = sum(len(pkg) for pkg in source_data["channels"].values())
    print(f"  {i}. {source_data['source_name']}: {source_total} قناة")
