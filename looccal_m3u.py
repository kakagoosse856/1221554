import aiohttp
import asyncio
import json
import time
import os
from datetime import datetime

# =========================================================
#  CONFIGURATION
# =========================================================

JSON_DB_URL = "https://oma-server.site/omar/db.json"
MY_NODE_KEY = "omar_094_key"  # هذا هو المفتاح الموجود في ملفك

# =========================================================

async def fetch_db_data():
    """تحميل قاعدة البيانات"""
    try:
        ts = int(time.time())
        url = f"{JSON_DB_URL}?t={ts}"
        print(f"📥 جاري التحميل من: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10, ssl=False) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    print("✅ تم تحميل البيانات بنجاح")
                    return data.get('streams', {})
                else:
                    print(f"❌ فشل التحميل - الحالة: {response.status}")
                    return {}
    except Exception as e:
        print(f"⚠️ خطأ في التحميل: {e}")
        return {}

async def generate_m3u():
    """توليد ملف M3U"""
    print("=" * 50)
    print("🚀 مولد ملفات M3U التلقائي")
    print(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 المفتاح المستخدم: {MY_NODE_KEY}")
    print("=" * 50)
    
    print("🔄 جاري تحميل البيانات...")
    db_streams = await fetch_db_data()
    
    if not db_streams:
        print("❌ لا توجد بيانات!")
        return False
    
    print(f"\n📊 إجمالي القنوات في الملف: {len(db_streams)}")
    
    # تصفية البثوث الخاصة بهذا النود فقط
    my_streams = {}
    for sid, s in db_streams.items():
        if s.get('node_key') == MY_NODE_KEY:
            my_streams[sid] = s
            print(f"  ✓ قناة مطابقة: {s.get('name')} (الحالة: {s.get('status')})")
    
    if not my_streams:
        print(f"\n❌ لا توجد قنوات للمفتاح: {MY_NODE_KEY}")
        return False
    
    # فصل القنوات المفعلة عن غير المفعلة
    active_streams = {sid: s for sid, s in my_streams.items() if s.get('status') == 'on'}
    inactive_streams = {sid: s for sid, s in my_streams.items() if s.get('status') != 'on'}
    
    print(f"\n✅ قنوات مفعلة: {len(active_streams)}")
    print(f"⏸️  قنوات غير مفعلة: {len(inactive_streams)}")
    
    # إنشاء محتوى M3U
    m3u_content = []
    m3u_content.append("#EXTM3U")
    m3u_content.append(f"#looccal_m3u: قنوات Omar - تم التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    m3u_content.append(f"#مجموع القنوات: {len(active_streams)}")
    m3u_content.append("")
    
    # إضافة القنوات المفعلة فقط
    for sid, conf in active_streams.items():
        name = conf.get('name', 'قناة بدون اسم')
        input_url = conf.get('input', '')
        platform = conf.get('platform', 'general')
        
        # البحث عن رابط الصورة من قسم overlays إذا كان موجوداً
        overlay_id = conf.get('overlay', '')
        overlay_url = ""
        if overlay_id and 'overlays' in db_data:
            overlay_url = db_data['overlays'].get(overlay_id, {}).get('url', '')
        
        if input_url:
            # إضافة معلومات القناة
            tvg_logo = f' tvg-logo="{overlay_url}"' if overlay_url else ''
            extinf = f'#EXTINF:-1 tvg-id="{sid}" tvg-name="{name}"{tvg_logo} group-title="{platform}",{name}'
            m3u_content.append(extinf)
            m3u_content.append(input_url)
            m3u_content.append("")
            print(f"  ✓ {name}")
    
    # حفظ الملف
    output_file = "looccal_m3u.m3u"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_content))
    
    print(f"\n✅ تم حفظ {len(active_streams)} قناة في {output_file}")
    
    # عرض محتوى الملف
    print("\n📄 محتوى ملف M3U:")
    print("-" * 50)
    with open(output_file, "r", encoding="utf-8") as f:
        print(f.read())
    print("-" * 50)
    
    return True

async def main():
    global db_data
    # تحميل البيانات كاملة للاستفادة من قسم overlays
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{JSON_DB_URL}?t={int(time.time())}", ssl=False) as response:
            if response.status == 200:
                db_data = await response.json(content_type=None)
    
    await generate_m3u()

if __name__ == "__main__":
    db_data = {}  # لتخزين البيانات الكاملة
    asyncio.run(main())
