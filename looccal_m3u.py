import aiohttp
import asyncio
import json
import time
import os
from datetime import datetime

# =========================================================
#  CONFIGURATION AREA
# =========================================================

# رابط ملف الداتا المباشر
JSON_DB_URL = "https://oma-server.site/omar/db.json"

# مفتاح الاستضافة الخاص بك
MY_NODE_KEY = "omar_094_key"  # غير هذا حسب مفتاحك

# =========================================================

async def fetch_db_data():
    """تحميل قاعدة البيانات"""
    try:
        ts = int(time.time())
        url = f"{JSON_DB_URL}?t={ts}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10, ssl=False) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    return data.get('streams', {})
                return {}
    except Exception as e:
        print(f"⚠️ خطأ في التحميل: {e}")
        return {}

async def generate_m3u():
    """توليد ملف M3U"""
    print("🔄 جاري تحميل البيانات...")
    db_streams = await fetch_db_data()
    
    if not db_streams:
        print("❌ لا توجد بيانات!")
        return False
    
    # تصفية البثوث الخاصة بهذا النود فقط
    my_streams = {}
    for sid, s in db_streams.items():
        if s.get('node_key') == MY_NODE_KEY and s.get('status') == 'on':
            my_streams[sid] = s
    
    if not my_streams:
        print(f"❌ لا توجد بثوث مفعلة للمفتاح: {MY_NODE_KEY}")
        return False
    
    print(f"✅ تم العثور على {len(my_streams)} بث مفعل")
    
    # إنشاء محتوى M3U
    m3u_content = []
    m3u_content.append("#EXTM3U")
    m3u_content.append(f"#PLAYLIST: قنواتي - تم التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    m3u_content.append("")
    
    for sid, conf in my_streams.items():
        name = conf.get('name', 'قناة بدون اسم')
        input_url = conf.get('input', '')
        logo = conf.get('logo', '')
        platform = conf.get('platform', 'general')
        
        if input_url:
            # إضافة معلومات القناة
            extinf = f'#EXTINF:-1 tvg-id="{sid}" tvg-name="{name}" tvg-logo="{logo}" group-title="{platform}",{name}'
            m3u_content.append(extinf)
            m3u_content.append(input_url)
            m3u_content.append("")
            print(f"  ✓ {name}")
    
    # حفظ الملف
    output_file = "looccal_m3u.m3u"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_content))
    
    print(f"\n✅ تم حفظ {len(my_streams)} قناة في {output_file}")
    return True

async def main():
    print("=" * 50)
    print("🚀 مولد ملفات M3U التلقائي")
    print(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 المفتاح المستخدم: {MY_NODE_KEY}")
    print("=" * 50)
    
    success = await generate_m3u()
    
    if success:
        # عرض محتوى الملف (أول 10 أسطر)
        print("\n📄 معاينة أول 10 أسطر من الملف:")
        print("-" * 30)
        with open("looccal_m3u.m3u", "r", encoding="utf-8") as f:
            lines = f.readlines()[:10]
            for line in lines:
                print(line.strip())
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())
