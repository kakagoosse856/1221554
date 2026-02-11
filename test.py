import requests
import xml.etree.ElementTree as ET
from io import BytesIO
import gzip
import os
import json
from datetime import datetime

print(f"🕐 بدأ التحديث: {datetime.now()}")

# قائمة URLs للـ EPG
epg_urls = [
    'https://vnepg.site/epg.xml',
    'https://epg.pw/api/epg.xml?lang=en&timezone=QXNpYS9Ib19DaGlfTWluaA%3D%3D&channel_id=369848',
    'https://epg.pw/api/epg.xml?lang=en&timezone=QXNpYS9Ib19DaGlfTWluaA%3D%3D&channel_id=9396',
]

# قائمة القنوات - يمكنك تعديلها
channels = [
    {
        'name': 'Animax',
        'url': 'http://example.com/animax.m3u8',
        'logo': 'https://example.com/animax.png',
        'epg_id': '369848',
        'group': 'ترفيه'
    },
    {
        'name': 'BabyTV',
        'url': 'http://example.com/babytv.m3u8',
        'logo': 'https://example.com/babytv.png',
        'epg_id': '9396',
        'group': 'أطفال'
    }
]

# ١. إنشاء ملف EPG المدمج
tv = ET.Element('tv')
success_count = 0
fail_count = 0

for i, url in enumerate(epg_urls, 1):
    try:
        print(f"📡 جاري تحميل EPG {i}/{len(epg_urls)}: {url[:50]}...")
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
        else:
            fail_count += 1
            print(f"❌ خطأ {response.status_code}: {url[:50]}...")
    except Exception as e:
        fail_count += 1
        print(f"⚠️ استثناء: {url[:50]}... - {str(e)[:50]}")

# حفظ ملف EPG
epg_file = 'epg.xml'
tree = ET.ElementTree(tv)
tree.write(epg_file, encoding='utf-8', xml_declaration=True)
epg_size = os.path.getsize(epg_file) / 1024
print(f"✅ تم حفظ EPG: {epg_file} ({epg_size:.2f} KB)")

# ٢. إنشاء ملف M3U
m3u_file = 'playlist.m3u'
repo_name = os.environ.get('GITHUB_REPOSITORY', 'username/repo')
m3u_url = f'https://raw.githubusercontent.com/{repo_name}/main/playlist.m3u'
epg_url = f'https://raw.githubusercontent.com/{repo_name}/main/epg.xml'

with open(m3u_file, 'w', encoding='utf-8') as f:
    # كتابة رأس M3U
    f.write('#EXTM3U\n')
    f.write(f'#EXTINF:-1 tvg-url="{epg_url}", EPG URL\n')
    f.write('# هذا الملف تم إنشاؤه تلقائياً بواسطة GitHub Actions\n')
    f.write(f'# تاريخ التحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    
    # إضافة كل قناة
    for channel in channels:
        group = channel.get('group', 'عام')
        f.write(f'#EXTINF:-1 tvg-id="{channel["epg_id"]}" tvg-name="{channel["name"]}" tvg-logo="{channel["logo"]}" group-title="{group}", {channel["name"]}\n')
        f.write(f'{channel["url"]}\n\n')

print(f"✅ تم حفظ M3U: {m3u_file} ({len(channels)} قناة)")

# ٣. تحديث README.md (بدون استخدام f-string متعدد الأسطر)
readme_file = 'README.md'
with open(readme_file, 'w', encoding='utf-8') as f:
    f.write('# 📺 قنوات IPTV مع EPG\n\n')
    f.write(f'آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    f.write('## 📋 روابط التحميل\n\n')
    f.write('🔗 **ملف M3U:**\n')
    f.write(f'```\n{m3u_url}\n```\n\n')
    f.write('🔗 **ملف EPG:**\n')
    f.write(f'```\n{epg_url}\n```\n\n')
    f.write('## 📊 الإحصائيات\n\n')
    f.write(f'- عدد القنوات: {len(channels)}\n')
    f.write(f'- حجم ملف EPG: {epg_size:.1f} KB\n')
    f.write(f'- تم تحميل EPG: {success_count} نجاح, {fail_count} فشل\n')
    f.write('- حالة التحديث: تلقائي كل 6 ساعات\n\n')
    f.write('## ⚙️ كيفية الاستخدام\n\n')
    f.write('1. انسخ رابط M3U\n')
    f.write('2. أضفه في مشغل IPTV (TiviMate, IPTV Pro, OTT Navigator)\n')
    f.write('3. أضف رابط EPG في إعدادات الدليل\n\n')
    f.write('## 📺 قائمة القنوات\n\n')
    
    for channel in channels:
        f.write(f'- **{channel["name"]}** (EPG ID: {channel["epg_id"]})\n')

print(f"✅ تم تحديث {readme_file}")

# ٤. إنشاء ملف channels.json (اختياري)
channels_file = 'channels.json'
with open(channels_file, 'w', encoding='utf-8') as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)
print(f"✅ تم حفظ {channels_file}")

print(f"\n📊 ملخص:")
print(f"   - EPG: {epg_file} ({epg_size:.2f} KB)")
print(f"   - M3U: {m3u_file} ({len(channels)} قناة)")
print(f"   - JSON: {channels_file}")
print(f"🕐 اكتمل: {datetime.now()}")
