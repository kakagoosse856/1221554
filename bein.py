import requests
import os
import re
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
# تصنيف القنوات الرياضية حسب الباقة
# =====================
SPORTS_PACKAGES = {
    # الباقات العربية
    "بي إن سبورت": {
        "keywords": ["bein", "beIN", "البي ان", "بي إن", "be in", "beIN Sports", "beIN"],
        "logo": "🇶🇦",
        "country": "قطر"
    },
    "SSC": {
        "keywords": ["ssc", "SSC", "السعودية", "Saudi Sports", "KSA Sports"],
        "logo": "🇸🇦",
        "country": "السعودية"
    },
    "أبوظبي الرياضية": {
        "keywords": ["ad sports", "أبوظبي", "abu dhabi", "AD Sports", "AD"],
        "logo": "🇦🇪",
        "country": "الإمارات"
    },
    "الكأس": {
        "keywords": ["alkass", "الكأس", "alkas", "Alkass", "Al Kass"],
        "logo": "🇶🇦",
        "country": "قطر"
    },
    "أون تايم سبورت": {
        "keywords": ["on time", "أون تايم", "ontime", "ONTime", "ON Time"],
        "logo": "🇪🇬",
        "country": "مصر"
    },
    "العراقية الرياضية": {
        "keywords": ["iraq", "العراقية", "الرياضية العراقية", "Iraq Sports", "Al Iraqia"],
        "logo": "🇮🇶",
        "country": "العراق"
    },
    "الأردن الرياضية": {
        "keywords": ["jordan", "الأردن", "Jordan Sports", "JRTV"],
        "logo": "🇯🇴",
        "country": "الأردن"
    },
    "الليبية الرياضية": {
        "keywords": ["libya", "الليبية", "ليبيا", "Libya Sports", "LBB"],
        "logo": "🇱🇾",
        "country": "ليبيا"
    },
    "المغربية الرياضية": {
        "keywords": ["morocco", "المغربية", "المغرب", "Morocco Sports", "SNRT"],
        "logo": "🇲🇦",
        "country": "المغرب"
    },
    "الجزائرية الرياضية": {
        "keywords": ["algeria", "الجزائرية", "الجزائر", "Algeria Sports", "EPTV"],
        "logo": "🇩🇿",
        "country": "الجزائر"
    },
    "التونسية الرياضية": {
        "keywords": ["tunisia", "التونسية", "تونس", "Tunisia Sports", "Wattania"],
        "logo": "🇹🇳",
        "country": "تونس"
    },
    "دبي الرياضية": {
        "keywords": ["dubai", "دبي", "Dubai Sports", "Dubai Racing"],
        "logo": "🇦🇪",
        "country": "الإمارات"
    },
    "الشارقة الرياضية": {
        "keywords": ["sharjah", "الشارقة", "Sharjah Sports"],
        "logo": "🇦🇪",
        "country": "الإمارات"
    },
    
    # الباقات العالمية
    "Sky Sports": {
        "keywords": ["sky sports", "sky", "سكاي", "Sky Sports", "Sky Sports UK"],
        "logo": "🇬🇧",
        "country": "بريطانيا"
    },
    "BT Sport": {
        "keywords": ["bt sport", "bt", "BT Sports", "BT Sport ESPN"],
        "logo": "🇬🇧",
        "country": "بريطانيا"
    },
    "DAZN": {
        "keywords": ["dazn", "DAZN", "دازون"],
        "logo": "🌍",
        "country": "عالمي"
    },
    "Arena Sport": {
        "keywords": ["arena", "Arena Sport", "أرينا", "Sport Klub"],
        "logo": "🇪🇺",
        "country": "أوروبا"
    },
    "Sport TV": {
        "keywords": ["sport tv", "SportTV", "Sport TV Portugal"],
        "logo": "🇵🇹",
        "country": "البرتغال"
    },
    "Eleven Sports": {
        "keywords": ["eleven", "Eleven Sports", "11 sports"],
        "logo": "🇪🇺",
        "country": "أوروبا"
    },
    "Match TV": {
        "keywords": ["match", "Match TV", "матч"],
        "logo": "🇷🇺",
        "country": "روسيا"
    },
    "Setanta Sports": {
        "keywords": ["setanta", "Setanta Sports", "سيتانتا"],
        "logo": "🇪🇺",
        "country": "أوروبا"
    },
    "ESPN": {
        "keywords": ["espn", "ESPN", "إي إس بي إن"],
        "logo": "🇺🇸",
        "country": "أمريكا"
    },
    "Fox Sports": {
        "keywords": ["fox", "Fox Sports", "فوكس"],
        "logo": "🇺🇸",
        "country": "أمريكا"
    },
    "NBC Sports": {
        "keywords": ["nbc", "NBC Sports"],
        "logo": "🇺🇸",
        "country": "أمريكا"
    },
    "CBS Sports": {
        "keywords": ["cbs", "CBS Sports"],
        "logo": "🇺🇸",
        "country": "أمريكا"
    },
    "TNT Sports": {
        "keywords": ["tnt", "TNT Sports"],
        "logo": "🇺🇸",
        "country": "أمريكا"
    },
    "Sport 1": {
        "keywords": ["sport 1", "Sport1", "Sport 1 Germany"],
        "logo": "🇩🇪",
        "country": "ألمانيا"
    },
    "Eurosport": {
        "keywords": ["eurosport", "Eurosport", "يوروسبورت"],
        "logo": "🇪🇺",
        "country": "أوروبا"
    },
    "Canal+ Sport": {
        "keywords": ["canal+", "Canal Plus", "Canal+ Sport"],
        "logo": "🇫🇷",
        "country": "فرنسا"
    },
    "RMC Sport": {
        "keywords": ["rmc", "RMC Sport"],
        "logo": "🇫🇷",
        "country": "فرنسا"
    },
    "Movistar+": {
        "keywords": ["movistar", "Movistar+"],
        "logo": "🇪🇸",
        "country": "إسبانيا"
    },
    "LaLiga TV": {
        "keywords": ["laliga", "LaLiga", "الليجا"],
        "logo": "🇪🇸",
        "country": "إسبانيا"
    },
    "Serie A": {
        "keywords": ["serie a", "Serie A", "الدوري الإيطالي"],
        "logo": "🇮🇹",
        "country": "إيطاليا"
    },
    "Bundesliga": {
        "keywords": ["bundesliga", "Bundesliga", "البوندسليجا"],
        "logo": "🇩🇪",
        "country": "ألمانيا"
    },
    "Ligue 1": {
        "keywords": ["ligue 1", "Ligue 1", "الدوري الفرنسي"],
        "logo": "🇫🇷",
        "country": "فرنسا"
    },
    "Premier League": {
        "keywords": ["premier league", "Premier League", "الدوري الإنجليزي", "EPL"],
        "logo": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "country": "إنجلترا"
    },
    
    # القنوات المتخصصة
    "Golf Channel": {
        "keywords": ["golf", "Golf Channel"],
        "logo": "⛳",
        "country": "عالمي"
    },
    "Tennis Channel": {
        "keywords": ["tennis", "Tennis Channel"],
        "logo": "🎾",
        "country": "عالمي"
    },
    "NBA TV": {
        "keywords": ["nba", "NBA TV"],
        "logo": "🏀",
        "country": "أمريكا"
    },
    "NFL Network": {
        "keywords": ["nfl", "NFL Network"],
        "logo": "🏈",
        "country": "أمريكا"
    },
    "MLB Network": {
        "keywords": ["mlb", "MLB Network"],
        "logo": "⚾",
        "country": "أمريكا"
    },
    "NHL Network": {
        "keywords": ["nhl", "NHL Network"],
        "logo": "🏒",
        "country": "أمريكا"
    },
    "UFC Fight Pass": {
        "keywords": ["ufc", "UFC", "fighting"],
        "logo": "🥊",
        "country": "عالمي"
    },
    "WWE Network": {
        "keywords": ["wwe", "WWE"],
        "logo": "🎭",
        "country": "عالمي"
    },
    "F1 TV": {
        "keywords": ["f1", "formula", "فورمولا"],
        "logo": "🏎️",
        "country": "عالمي"
    },
    "MotoGP": {
        "keywords": ["motogp", "MotoGP"],
        "logo": "🏍️",
        "country": "عالمي"
    },
    "Olympic Channel": {
        "keywords": ["olympic", "Olympic Channel", "أولمبي"],
        "logo": "🏅",
        "country": "عالمي"
    }
}

# كلمات عامة للقنوات الرياضية
GENERIC_SPORTS_KEYWORDS = [
    "sport", "الرياضية", "رياضة", "sports", "spor", "hd", "4k", 
    "كأس", "كاس", "كورة", "kora", "football", "كرة قدم", "match",
    "مباراة", "دوري", "league", "champions", "بطولة", "كأس العالم"
]

OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bein_auto.m3u8")

def identify_package(channel_name, url_text):
    """تحديد الباقة الرياضية التي تنتمي لها القناة"""
    combined = (channel_name + " " + url_text).lower()
    
    for package_name, package_info in SPORTS_PACKAGES.items():
        for keyword in package_info["keywords"]:
            if keyword.lower() in combined:
                return package_name, package_info
    
    # إذا لم يتم العثور على باقة محددة، تحقق إذا كانت قناة رياضية عامة
    for keyword in GENERIC_SPORTS_KEYWORDS:
        if keyword.lower() in combined:
            return "رياضية عامة", {"logo": "⚽", "country": "عالمي"}
    
    return None, None

print("=" * 60)
print("📡  باقة القنوات الرياضية العالمية والعربية")
print("=" * 60)

# هيكل البيانات: [package][server][channel_name] = set(urls)
all_channels = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

for idx, src in enumerate(SOURCES, start=1):
    server_name = f"SERVER {idx}"
    
    print(f"\n[INFO] تحميل {server_name}: {src}")
    try:
        response = requests.get(src, timeout=20)
        response.encoding = 'utf-8'
        lines = response.text.splitlines()
    except Exception as e:
        print(f"[ERROR] فشل تحميل {src}: {e}")
        continue

    channels_found = 0
    for i, line in enumerate(lines):
        if not line.startswith("#EXTINF") or i + 1 >= len(lines):
            continue

        url = lines[i + 1].strip()
        
        # التحقق من صحة الرابط
        if not url.lower().endswith(".m3u8"):
            continue

        # استخراج اسم القناة
        name_match = re.search(r'#EXTINF:-?[0-9]*.*?,(.*)', line)
        if name_match:
            channel_name = name_match.group(1).strip()
        else:
            # استخراج الاسم من الرابط
            url_parts = url.split('/')
            channel_name = url_parts[-1].replace('.m3u8', '').replace('_', ' ').replace('-', ' ').title()
        
        # تنظيف الاسم
        channel_name = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\-]', '', channel_name)
        channel_name = re.sub(r'\s+', ' ', channel_name).strip()
        
        if not channel_name or len(channel_name) < 2:
            continue

        # تحديد الباقة
        package_name, package_info = identify_package(channel_name, url)
        
        if package_name:
            # فحص الرابط
            try:
                r = requests.head(url, timeout=5, allow_redirects=True)
                if r.status_code != 200:
                    continue
            except:
                continue
            
            # حفظ القناة
            all_channels[package_name][server_name][channel_name].add(url)
            channels_found += 1
            print(f"  ✅ {package_info['logo']} {package_name} | {channel_name}")
    
    print(f"  📊 تم العثور على {channels_found} قناة في {server_name}")

# =====================
# إنشاء ملف M3U النهائي
# =====================
print("\n" + "=" * 60)
print("📝  جاري إنشاء ملف القنوات النهائي...")
print("=" * 60)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write('#EXTINF:-1 tvg-logo="https://i.imgur.com/QLz1Z3U.png" group-title="📡 جميع القنوات الرياضية",باقة القنوات الرياضية العالمية\n')
    f.write("https://example.com/placeholder.m3u8\n")  # Placeholder
    
    total_packages = 0
    total_channels = 0
    
    # ترتيب الباقات أبجدياً
    for package_name in sorted(all_channels.keys()):
        package_info = SPORTS_PACKAGES.get(package_name, {"logo": "📡", "country": "عالمي"})
        package_logo = package_info["logo"]
        package_country = package_info.get("country", "")
        
        package_channels = 0
        print(f"\n📦 {package_logo} {package_name} ({package_country})")
        
        for server_name in sorted(all_channels[package_name].keys()):
            for channel_name in sorted(all_channels[package_name][server_name].keys()):
                urls = all_channels[package_name][server_name][channel_name]
                for url in sorted(urls):
                    # إنشاء اسم جميل للقناة
                    clean_name = channel_name
                    if package_name not in clean_name:
                        clean_name = f"{package_logo} {clean_name}"
                    
                    f.write(
                        f'#EXTINF:-1 group-title="{package_logo} {package_name} | {server_name}",{clean_name}\n'
                    )
                    f.write(url + "\n")
                    package_channels += 1
                    total_channels += 1
        
        print(f"  └─ {package_channels} قناة")
        total_packages += 1

# =====================
# عرض الإحصائيات النهائية
# =====================
print("\n" + "=" * 60)
print("📊  إحصائيات الباقة النهائية")
print("=" * 60)
print(f"📦 عدد الباقات الرياضية: {total_packages}")
print(f"📺 إجمالي القنوات: {total_channels}")
print(f"💾 ملف الإخراج: {OUTPUT_FILE}")

print("\n📋  تفاصيل الباقات:")
for package_name, servers_data in sorted(all_channels.items()):
    package_info = SPORTS_PACKAGES.get(package_name, {"logo": "📡", "country": "عالمي"})
    total = sum(len(channels) for channels in servers_data.values())
    print(f"\n{package_info['logo']} {package_name} ({package_info['country']}):")
    print(f"  └─ {total} قناة")
    
    # عرض أول 3 قنوات كمثال
    example_channels = []
    for server_data in servers_data.values():
        for ch_name in list(server_data.keys())[:3]:
            example_channels.append(ch_name)
            if len(example_channels) >= 3:
                break
        if len(example_channels) >= 3:
            break
    
    for ex in example_channels:
        print(f"     • {ex}")

print("\n" + "=" * 60)
print("✅  تم الانتهاء بنجاح!")
print("=" * 60)
