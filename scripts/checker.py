#!/usr/bin/env python3
"""
M3U Playlist Checker - Simple Version
Checks M3U playlists and merges them
"""

import requests
import json
import os
from datetime import datetime

def load_urls():
    """تحميل الروابط من playlists.json أو استخدام الافتراضية"""
    urls = []
    
    # محاولة قراءة من playlists.json
    if os.path.exists('playlists.json'):
        try:
            with open('playlists.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # جمع كل الروابط
                if 'sources' in data:
                    urls.extend(data['sources'])
                if 'backup_sources' in data:
                    urls.extend(data['backup_sources'])
                    
                # إزالة التكرارات والقيم الفارغة
                urls = list(set([url for url in urls if url and isinstance(url, str)]))
                
        except Exception as e:
            print(f"⚠️ Error reading playlists.json: {e}")
            urls = []
    
    # إذا لم توجد روابط، استخدم الروابط الافتراضية
    if not urls:
        urls = [
            "https://raw.githubusercontent.com/kakagoosse856/1221554/2a5d587b525902b4a5fa4e13c977136839247f43/SSULTAN.m3u",
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u"
        ]
        print("ℹ️ Using default URLs")
    
    return urls

def check_url(url):
    """فحص رابط M3U"""
    try:
        print(f"🔍 Checking: {url[:60]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (M3U-Checker/1.0)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            # التحقق من أن الملف هو M3U صالح
            if '#EXTM3U' in content:
                # عد القنوات
                lines = content.split('\n')
                channels = [line for line in lines if line.startswith('#EXTINF')]
                
                return {
                    'status': 'valid',
                    'channels': len(channels),
                    'content': content,
                    'error': None
                }
            else:
                return {
                    'status': 'invalid',
                    'channels': 0,
                    'content': None,
                    'error': 'Not a valid M3U file'
                }
        else:
            return {
                'status': 'error',
                'channels': 0,
                'content': None,
                'error': f'HTTP {response.status_code}'
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'channels': 0,
            'content': None,
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'status': 'error',
            'channels': 0,
            'content': None,
            'error': str(e)
        }

def extract_channels(content):
    """استخراج القنوات من محتوى M3U"""
    channels = []
    lines = content.split('\n')
    
    for i in range(len(lines)):
        if lines[i].startswith('#EXTINF'):
            if i + 1 < len(lines) and lines[i + 1].startswith('http'):
                channels.append(lines[i])    # معلومات القناة
                channels.append(lines[i + 1]) # رابط القناة
    
    return channels

def main():
    print("=" * 60)
    print("🎬 M3U PLAYLIST CHECKER")
    print("=" * 60)
    
    # تحميل الروابط
    urls = load_urls()
    print(f"📡 Found {len(urls)} playlist(s) to check")
    
    # فحص كل رابط
    results = []
    all_channels = []
    valid_count = 0
    
    for url in urls:
        result = check_url(url)
        result['url'] = url
        results.append(result)
        
        if result['status'] == 'valid':
            valid_count += 1
            print(f"   ✅ Valid ({result['channels']} channels)")
            
            # استخراج القنوات
            if result['content']:
                channels = extract_channels(result['content'])
                all_channels.extend(channels)
        else:
            print(f"   ❌ {result['status'].title()}: {result['error']}")
    
    # إنشاء الملف المدمج
    if all_channels:
        # إزالة التكرارات (استناداً إلى رابط القناة)
        unique_channels = []
        seen_urls = set()
        
        i = 0
        while i < len(all_channels):
            if all_channels[i].startswith('#EXTINF') and i + 1 < len(all_channels):
                channel_url = all_channels[i + 1]
                if channel_url not in seen_urls:
                    seen_urls.add(channel_url)
                    unique_channels.append(all_channels[i])
                    unique_channels.append(channel_url)
                i += 2
            else:
                i += 1
        
        # كتابة الملف
        header = "#EXTM3U\n"
        header += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Sources: {valid_count}/{len(urls)}\n"
        header += f"# Unique Channels: {len(unique_channels)//2}\n"
        header += f"# Checker: GitHub Actions\n\n"
        
        with open('merged_channels.m3u', 'w', encoding='utf-8') as f:
            f.write(header)
            f.write('\n'.join(unique_channels))
        
        print(f"\n✅ SUCCESS: Created merged_channels.m3u")
        print(f"   📊 Statistics:")
        print(f"   - Valid playlists: {valid_count}/{len(urls)}")
        print(f"   - Unique channels: {len(unique_channels)//2}")
    else:
        with open('merged_channels.m3u', 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n# No valid playlists found\n")
        
        print(f"\n❌ No valid playlists found")
    
    # حفظ النتائج في ملف JSON
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_urls': len(urls),
            'valid_urls': valid_count,
            'failed_urls': len(urls) - valid_count,
            'unique_channels': len(all_channels)//2 if all_channels else 0
        },
        'results': results
    }
    
    with open('check_results.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Files saved:")
    print(f"   - merged_channels.m3u")
    print(f"   - check_results.json")
    print("=" * 60)
    print("✅ Process completed successfully!")
    
    # إرجاع النتيجة لـ GitHub Actions
    exit(0 if valid_count > 0 else 1)

if __name__ == "__main__":
    main()
