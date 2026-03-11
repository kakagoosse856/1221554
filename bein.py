import requests
import os
import re

# =====================
# مصادر القنوات
# =====================
SOURCES = [  
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/s1.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser1.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/ser6.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv4.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv5.m3u8",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/serv8.m3u8",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/xtrem2.m3u8",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/xxterrm.m3u",
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/m3u/xxterrm.m3u",
]

KEYWORD = "bein"
OUTPUT_DIR = "channels"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bein_auto.m3u8")

servers = {}

print("[INFO] استخراج قنوات BEIN وترتيبها حسب السيرفر فقط .m3u8...")

for idx, src in enumerate(SOURCES, start=1):
    server_name = f"SERVER {idx}"
    servers[server_name] = {}

    print(f"[INFO] تحميل {server_name}: {src}")
    try:
        response = requests.get(src, timeout=20)
        response.encoding = 'utf-8'
        lines = response.text.splitlines()
    except Exception as e:
        print(f"[ERROR] فشل تحميل {src}: {e}")
        continue

    for i, line in enumerate(lines):
        if not line.startswith("#EXTINF") or i + 1 >= len(lines):
            continue

        url = lines[i + 1].strip()
        if not url.lower().endswith(".m3u8"):
            continue

        if KEYWORD not in line.lower() and KEYWORD not in url.lower():
            continue

        # استخراج اسم القناة الأصلي بالكامل
        name_match = re.search(r'#EXTINF:-?[0-9]*.*?,(.*)', line)
        if name_match:
            channel_name = name_match.group(1).strip()
        else:
            # محاولة استخراج الاسم من الرابط كحل بديل
            url_parts = url.split('/')
            for part in url_parts:
                if 'bein' in part.lower() and any(x in part.lower() for x in ['sport', 'max', 'hd', '4k', 'sd', 'premium']):
                    channel_name = part.replace('.m3u8', '').replace('_', ' ').replace('-', ' ').title()
                    break
            else:
                channel_name = "beIN Sports"

        # تنظيف الاسم من الرموز الزائدة
        channel_name = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\-]', '', channel_name)
        channel_name = re.sub(r'\s+', ' ', channel_name).strip()

        # فحص الرابط
        try:
            r = requests.head(url, timeout=6, allow_redirects=True)
            if r.status_code != 200:
                continue
        except:
            continue

        # حفظ القناة باسمها الأصلي
        servers[server_name].setdefault(channel_name, set()).add(url)
        print(f"[OK] {server_name} | {channel_name}")

# =====================
# إنشاء ملف M3U النهائي مع الاحتفاظ بالأسماء الأصلية
# =====================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

    for server, channels in servers.items():
        for channel_name in sorted(channels.keys()):
            for url in sorted(channels[channel_name]):
                f.write(
                    f'#EXTINF:-1 group-title="✪ BEIN AUTO | {server}",{channel_name}\n'
                )
                f.write(url + "\n")

print(f"[DONE] تم إنشاء الباقة: {OUTPUT_FILE}")
print(f"[INFO] عدد السيرفرات: {len(servers)}")

# عرض بعض الإحصائيات
total_channels = sum(len(channels) for channels in servers.values())
print(f"[INFO] إجمالي القنوات الفريدة: {total_channels}")

# عرض أسماء القنوات الموجودة
print("\n[INFO] القنوات المستخرجة:")
all_channels = set()
for server, channels in servers.items():
    for channel_name in channels.keys():
        all_channels.add(channel_name)

for channel in sorted(all_channels):
    print(f"  • {channel}")
