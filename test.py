import requests
import xml.etree.ElementTree as ET
from io import BytesIO
import gzip
import os
from datetime import datetime

# قائمة URLs للـ EPG
epg_urls = [
    'https://vnepg.site/epg.xml',
    # ... باقي روابط EPG
]

# قائمة قنواتك - يمكنك إضافة قنواتك هنا
channels = [
    {
        'name': 'beIN SPORTS 1',
        'url': 'http://your-server.com/bein1.m3u8',
        'logo': 'https://example.com/bein1.png',
        'epg_id': '443147'
    },
    {
        'name': 'beIN SPORTS 2',
        'url': 'http://your-server.com/bein2.m3u8',
        'logo': 'https://example.com/bein2.png',
        'epg_id': '443147'
    },
    {
        'name': 'Sky Sports Football',
        'url': 'http://your-server.com/skyfootball.m3u8',
        'logo': 'https://example.com/skyfootball.png',
        'epg_id': '450289'
    },
    # ... أضف المزيد من القنوات
]

print(f"🕐 بدأ التحديث: {datetime.now()}")

# ١. إنشاء ملف EPG المدمج
tv = ET.Element('tv')
success_count = 0

for i, url in enumerate(epg_urls, 1):
    try:
        print(f"📡 جاري تحميل EPG {i}/{len(epg_urls)}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            if url.endswith('.gz'):
                with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8') as f:
                    tree = ET.parse(f)
            else:
                tree = ET.parse(BytesIO(response.content))
                
            root = tree.getroot()
            for elem in root:
                tv.append(elem)
            success_count += 1
            print(f"✅ تم تحميل EPG: {url[:50]}...")
    except Exception as e:
        print(f"⚠️ خطأ: {url[:50]}... - {str(e)[:50]}")

# حفظ ملف EPG
epg_file = 'epg.xml'
tree = ET.ElementTree(tv)
tree.write(epg_file, encoding='utf-8', xml_declaration=True)
print(f"✅ تم حفظ EPG: {epg_file}")

# ٢. إنشاء ملف M3U
m3u_file = 'playlist.m3u'
m3u_url = 'https://raw.githubusercontent.com/اسم-المستخدم/اسم-المستودع/main/playlist.m3u'
epg_url = 'https://raw.githubusercontent.com/اسم-المستخدم/اسم-المستودع/main/epg.xml'

with open(m3u_file, 'w', encoding='utf-8') as f:
    # كتابة رأس M3U
    f.write('#EXTM3U\n')
    f.write(f'#EXTINF:-1 tvg-url="{epg_url}", EPG URL\n')
    f.write('# هذا الملف تم إنشاؤه تلقائياً\n\n')
    
    # إضافة كل قناة
    for channel in channels:
        # معلومات القناة
        f.write(f'#EXTINF:-1 tvg-id="{channel["epg_id"]}" tvg-name="{channel["name"]}" tvg-logo="{channel["logo"]}" group-title="رياضة", {channel["name"]}\n')
        f.write(f'{channel["url"]}\n\n')

print(f"✅ تم حفظ M3U: {m3u_file} ({len(channels)} قناة)")

# ٣. تحديث README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(f'''# 📺 قنوات IPTV مع EPG

آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 روابط التحميل

🔗 **ملف M3U:**
