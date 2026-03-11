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
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser1.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser6.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv4.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv5.m3u8",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv8.m3u8",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/xtrem2.m3u8",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/xxterrm.m3u",
]

# =====================
# تصنيف القنوات الرياضية
# =====================
SPORTS_PACKAGES = {
    # الباقات العربية
    "بي إن سبورت": {"keywords": ["bein", "beIN", "البي ان", "بي إن"], "logo": "🇶🇦"},
    "SSC": {"keywords": ["ssc", "SSC", "السعودية"], "logo": "🇸🇦"},
    "أبوظبي الرياضية": {"keywords": ["ad sports", "أبوظبي", "abu dhabi"], "logo": "🇦🇪"},
    "الكأس": {"keywords": ["alkass", "الكأس", "alkas"], "logo": "🇶🇦"},
    "أون تايم سبورت": {"keywords": ["on time", "أون تايم", "ontime"], "logo": "🇪🇬"},
    "العراقية الرياضية": {"keywords": ["iraq", "العراقية"], "logo": "🇮🇶"},
    
    # الباقات العالمية
    "Sky Sports": {"keywords": ["sky sports", "sky"], "logo": "🇬🇧"},
    "BT Sport": {"keywords": ["bt sport"], "logo": "🇬🇧"},
    "DAZN": {"keywords": ["dazn"], "logo": "🌍"},
    "ESPN": {"keywords": ["espn"], "logo": "🇺🇸"},
    "Eurosport": {"keywords": ["eurosport"], "logo": "🇪🇺"},
}

OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_sports.m3u8")

def identify_package(text):
    """تحديد الباقة الرياضية"""
    text = text.lower()
    for package, info in SPORTS_PACKAGES.items():
        for keyword in info["keywords"]:
            if keyword.lower() in text:
                return package, info["logo"]
    return "رياضية عامة", "⚽"

print("🚀 بدء استخراج القنوات الرياضية...")

all_channels = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

for idx, src in enumerate(SOURCES, start=1):
    server = f"SRV{idx}"
    print(f"📡 تحميل {server}...")
    
    try:
        r = requests.get(src, timeout=15)
        lines = r.text.splitlines()
    except:
        print(f"❌ فشل تحميل {src}")
        continue
    
    for i, line in enumerate(lines):
        if not line.startswith("#EXTINF") or i+1 >= len(lines):
            continue
        
        url = lines[i+1].strip()
        if not url.endswith(".m3u8"):
            continue
        
        # استخراج الاسم
        name_match = re.search(r'#EXTINF:-?[0-9]*.*?,(.*)', line)
        name = name_match.group(1).strip() if name_match else "قناة رياضية"
        
        # تنظيف الاسم
        name = re.sub(r'[^\w\s\u0600-\u06FF]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        if not name:
            continue
        
        # تحديد الباقة
        package, logo = identify_package(name + " " + url)
        
        # فحص الرابط (اختصار للوقت)
        if idx <= 3:  # نفحص فقط أول 3 سيرفرات لتوفير الوقت
            try:
                r2 = requests.head(url, timeout=3)
                if r2.status_code != 200:
                    continue
            except:
                continue
        
        # حفظ القناة
        all_channels[package][server][name].add(url)
        print(f"  ✅ {logo} {name[:40]}...")

# =====================
# إنشاء الملف النهائي
# =====================
print("\n📝 إنشاء ملف M3U...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    
    total = 0
    for package in sorted(all_channels.keys()):
        logo = SPORTS_PACKAGES.get(package, {}).get("logo", "⚽")
        
        for server in sorted(all_channels[package].keys()):
            for name in sorted(all_channels[package][server].keys()):
                urls = list(all_channels[package][server][name])
                if urls:
                    f.write(f'#EXTINF:-1 group-title="{logo} {package}",{name}\n')
                    f.write(urls[0] + "\n")
                    total += 1
    
    print(f"✅ تم إنشاء {total} قناة في {OUTPUT_FILE}")

# =====================
# إنشاء ملف بسيط للـ beIN فقط (للتوافق مع الكود القديم)
# =====================
BEIN_FILE = os.path.join(OUTPUT_DIR, "all_sports.m3u8")
with open(BEIN_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    bein_count = 0
    
    for package in ["بي إن سبورت"]:
        if package in all_channels:
            for server in all_channels[package]:
                for name in all_channels[package][server]:
                    urls = list(all_channels[package][server][name])
                    if urls:
                        f.write(f'#EXTINF:-1 group-title="🇶🇦 {package}",{name}\n')
                        f.write(urls[0] + "\n")
                        bein_count += 1
    
    print(f"✅ تم إنشاء {bein_count} قناة beIN في {BEIN_FILE}")

print("\n🎉 تم الانتهاء بنجاح!")
