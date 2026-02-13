import requests
import json
from datetime import datetime

# =========================================================
#  الإعدادات
# =========================================================

JSON_DB_URL = "https://oma-server.site/omar/db.json"
OUTPUT_FILE = "playlist.m3u"

# =========================================================

def fetch_data():
    """تحميل بيانات القنوات"""
    try:
        print("📥 جاري تحميل البيانات...")
        response = requests.get(JSON_DB_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ تم تحميل البيانات بنجاح")
            return data
        else:
            print(f"❌ فشل التحميل - الحالة: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
        return None

def extract_all_channels(data):
    """استخراج جميع القنوات من البيانات"""
    streams = data.get('streams', {})
    overlays = data.get('overlays', {})
    
    channels = []
    
    print(f"\n📊 إجمالي القنوات في قاعدة البيانات: {len(streams)}")
    print("-" * 60)
    
    for stream_id, stream_data in streams.items():
        # بيانات القناة
        name = stream_data.get('name', 'بدون اسم')
        status = stream_data.get('status', 'off')
        input_url = stream_data.get('input', '')
        platform = stream_data.get('platform', 'غير معروف')
        node_key = stream_data.get('node_key', 'بدون مفتاح')
        
        # الحصول على رابط الشعار إذا وجد
        overlay_id = stream_data.get('overlay', '')
        logo_url = overlays.get(overlay_id, {}).get('url', '') if overlay_id else ''
        
        # حالة القناة (🟢 مفعلة / 🔴 غير مفعلة)
        status_icon = "🟢" if status == 'on' else "🔴"
        
        # إضافة القناة (جميع القنوات بدون فلترة)
        channels.append({
            'id': stream_id,
            'name': name,
            'url': input_url,
            'logo': logo_url,
            'platform': platform,
            'status': status,
            'node_key': node_key,
            'status_icon': status_icon
        })
        
        # طباعة معلومات القناة
        print(f"  {status_icon} {name}")
        print(f"     ├─ المنصة: {platform}")
        print(f"     ├─ المفتاح: {node_key}")
        print(f"     └─ الحالة: {status}")
    
    return channels

def create_m3u_file(channels, filename=OUTPUT_FILE):
    """إنشاء ملف M3U بجميع القنوات"""
    print(f"\n📝 جاري إنشاء ملف {filename}...")
    
    if not channels:
        print("❌ لا توجد قنوات!")
        return False
    
    # إحصائيات
    total = len(channels)
    active = len([c for c in channels if c['status'] == 'on'])
    inactive = total - active
    
    with open(filename, 'w', encoding='utf-8') as f:
        # رأس الملف
        f.write("#EXTM3U\n")
        f.write(f"#PLAYLIST: جميع القنوات - تم التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"#إجمالي القنوات: {total} (مفعل: {active} | غير مفعل: {inactive})\n\n")
        
        # كتابة كل قناة
        for ch in channels:
            # إضافة علامة للقنوات غير المفعلة
            name_display = ch['name']
            if ch['status'] != 'on':
                name_display += " [غير مفعلة]"
            
            logo_part = f' tvg-logo="{ch["logo"]}"' if ch['logo'] else ''
            extinf = f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}"{logo_part} group-title="{ch["platform"]}",{name_display}'
            f.write(extinf + "\n")
            f.write(ch['url'] + "\n\n")
        
        # كتابة إحصائيات في نهاية الملف
        f.write(f"\n# ================ إحصائيات ================\n")
        f.write(f"# تم التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# إجمالي القنوات: {total}\n")
        f.write(f"# القنوات المفعلة: {active}\n")
        f.write(f"# القنوات غير المفعلة: {inactive}\n")
        f.write(f"# =========================================\n")
    
    print(f"✅ تم إنشاء الملف بنجاح!")
    return total, active, inactive

def main():
    print("=" * 70)
    print("🎬 مستخرج جميع القنوات M3U".center(70))
    print("=" * 70)
    print(f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 مصدر البيانات: {JSON_DB_URL}")
    print("-" * 70)
    
    # تحميل البيانات
    data = fetch_data()
    if not data:
        return
    
    # استخراج جميع القنوات
    channels = extract_all_channels(data)
    
    if channels:
        print(f"\n✅ تم العثور على {len(channels)} قناة في قاعدة البيانات")
        
        # إنشاء ملف M3U
        total, active, inactive = create_m3u_file(channels)
        
        print(f"\n📄 تم حفظ الملف في: {OUTPUT_FILE}")
        print(f"\n📊 ملخص:")
        print(f"   ├─ إجمالي القنوات: {total}")
        print(f"   ├─ قنوات مفعلة: {active}")
        print(f"   └─ قنوات غير مفعلة: {inactive}")
        
        # عرض محتوى الملف
        print(f"\n📋 معاينة أول 15 سطر من الملف:")
        print("-" * 70)
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:15]
            for line in lines:
                print(line.strip())
        print("-" * 70)
        
        print(f"\n🌐 رابط الملف المباشر:")
        print(f"   {OUTPUT_FILE}")
        print(f"\n💡 يمكنك فتح هذا الملف في VLC أو أي مشغل IPTV")

if __name__ == "__main__":
    main()
