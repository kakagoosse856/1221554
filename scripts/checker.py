#!/usr/bin/env python3
"""
M3U Playlist Checker for GitHub Actions - Updated for GHA new syntax
"""

import requests
import sys
import json
import os
from datetime import datetime
import time

def validate_m3u_content(content):
    """التحقق من محتوى M3U"""
    lines = content.strip().split('\n')
    
    if not lines or not lines[0].startswith('#EXTM3U'):
        return False, 0, []
    
    channels = []
    current_channel = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('#EXTINF'):
            # استخراج معلومات القناة
            parts = line.split(',', 1)
            channel_info = {
                'duration': parts[0].split(':')[1] if ':' in parts[0] else '',
                'name': parts[1] if len(parts) > 1 else 'Unknown',
                'raw_info': line
            }
            current_channel = {'info': channel_info}
            
        elif line and not line.startswith('#') and current_channel:
            # هذا هو رابط القناة
            current_channel['url'] = line
            channels.append(current_channel.copy())
            current_channel = {}
    
    return True, len(channels), channels

def check_m3u_url(url, timeout=15):
    """فحص رابط M3U مع إعادة المحاولة"""
    max_retries = 2
    
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; M3U-Checker/2.0)'
            }
            
            print(f"🔄 Attempt {attempt + 1}/{max_retries}: {url[:50]}...")
            
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                is_valid, count, channels = validate_m3u_content(response.text)
                
                if is_valid:
                    print(f"✅ Valid: {count} channels found")
                    return {
                        'status': 'valid',
                        'channels_count': count,
                        'content': response.text,
                        'response_time': response.elapsed.total_seconds(),
                        'size_kb': len(response.content) / 1024
                    }
                else:
                    print(f"❌ Invalid M3U format")
                    return {
                        'status': 'invalid_format',
                        'response_time': response.elapsed.total_seconds()
                    }
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return {
                    'status': 'http_error',
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                return {'status': 'timeout'}
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                return {'status': 'connection_error'}
        except Exception as e:
            print(f"⚠️ Error: {str(e)[:50]}")
            if attempt == max_retries - 1:
                return {'status': 'error', 'message': str(e)}
        
        if attempt < max_retries - 1:
            time.sleep(2)
    
    return {'status': 'failed'}

def merge_playlists(playlists_data):
    """دمج قوائم التشغيل مع إزالة التكرارات"""
    if not playlists_data:
        return "#EXTM3U\n# No valid playlists found\n"
    
    merged_header = "#EXTM3U"
    merged_channels = []
    seen_urls = set()
    total_channels = 0
    
    for playlist in playlists_data:
        if playlist['status'] == 'valid' and 'content' in playlist:
            lines = playlist['content'].strip().split('\n')
            
            if lines and lines[0].startswith('#EXTM3U'):
                i = 1
                while i < len(lines):
                    if lines[i].startswith('#EXTINF'):
                        info_line = lines[i]
                        
                        # البحث عن رابط القناة التالي
                        if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith('#'):
                            channel_url = lines[i + 1].strip()
                            
                            if channel_url not in seen_urls:
                                seen_urls.add(channel_url)
                                merged_channels.append(info_line)
                                merged_channels.append(channel_url)
                                total_channels += 1
                            
                            i += 2
                        else:
                            i += 1
                    else:
                        i += 1
    
    # إضافة التعليقات التوضيحية
    comments = []
    comments.append(f"\n# Generated by GitHub Actions")
    comments.append(f"# Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    comments.append(f"# Total Unique Channels: {total_channels}")
    comments.append(f"# Sources: {len(playlists_data)}")
    comments.append("#")
    
    for playlist in playlists_data:
        if playlist['status'] == 'valid':
            comments.append(f"# Source: {playlist.get('url', 'Unknown')[:50]}...")
            comments.append(f"#   Channels: {playlist.get('channels_count', 0)}")
    
    comments.append("")
    
    return merged_header + '\n'.join(comments) + '\n'.join(merged_channels)

def load_urls_from_json():
    """قراءة الروابط من playlists.json"""
    try:
        if os.path.exists('playlists.json'):
            with open('playlists.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            urls = config.get('sources', [])
            # إضافة المصادر الاحتياطية فقط إذا كانت المصادر الرئيسية فارغة
            if not urls:
                urls = config.get('backup_sources', [])
            else:
                urls.extend(config.get('backup_sources', []))
            
            return list(set(urls))  # إزالة التكرارات
    except Exception as e:
        print(f"⚠️ Error loading playlists.json: {e}")
    
    return None

def main():
    print("=" * 60)
    print("M3U PLAYLIST CHECKER - GitHub Actions")
    print("=" * 60)
    
    # محاولة قراءة الروابط من playlists.json أولاً
    urls = load_urls_from_json()
    
    # إذا لم يكن هناك ملف JSON، استخدم command line arguments
    if not urls and len(sys.argv) > 1:
        urls_input = sys.argv[1]
        urls = []
        for part in urls_input.replace(',', ' ').split():
            url = part.strip()
            if url and url.startswith('http'):
                urls.append(url)
    
    # إذا لم توجد روابط، استخدم القيمة الافتراضية
    if not urls:
        urls = [
            "https://raw.githubusercontent.com/kakagoosse856/1221554/2a5d587b525902b4a5fa4e13c977136839247f43/SSULTAN.m3u"
        ]
        print("ℹ️ Using default URL")
    
    print(f"📡 Checking {len(urls)} playlist(s)")
    print("-" * 60)
    
    results = []
    valid_playlists = []
    
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] {url}")
        
        result = check_m3u_url(url)
        result['url'] = url
        
        results.append(result)
        
        if result['status'] == 'valid':
            valid_playlists.append(result)
    
    # دمج القوائم الصالحة
    if valid_playlists:
        merged_content = merge_playlists(valid_playlists)
        
        # حفظ الملف المدمج
        with open('merged_channels.m3u', 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        print(f"\n✅ SUCCESS: Created merged_channels.m3u")
        print(f"   - Valid playlists: {len(valid_playlists)}/{len(urls)}")
        print(f"   - Total channels: {len([c for c in merged_content.split('\n') if c.startswith('http')])}")
        
        # حفظ النتائج كـ JSON
        output_data = {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_urls_checked': len(urls),
                'valid_urls': len(valid_playlists),
                'failed_urls': len(urls) - len(valid_playlists)
            },
            'details': results
        }
        
    else:
        print(f"\n❌ FAILED: No valid playlists found")
        merged_content = "#EXTM3U\n# No valid playlists found\n"
        
        with open('merged_channels.m3u', 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        output_data = {
            'success': False,
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_urls_checked': len(urls),
                'valid_urls': 0,
                'failed_urls': len(urls)
            },
            'details': results
        }
    
    # حفظ النتائج
    with open('check_results.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # كتابة output للـ GitHub Actions (الطريقة الحديثة)
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'STATUS={"SUCCESS" if output_data["success"] else "FAILED"}', file=fh)
            print(f'VALID_PLAYLISTS={len(valid_playlists)}', file=fh)
            print(f'TOTAL_URLS={len(urls)}', file=fh)
    
    print("\n" + "=" * 60)
    print("✅ Process completed!")
    print(f"📁 Output files:")
    print(f"   - merged_channels.m3u")
    print(f"   - check_results.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
