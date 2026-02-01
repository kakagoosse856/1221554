#!/usr/bin/env python3
"""
M3U Playlist Checker for GitHub Actions
"""

import requests
import sys
import json
import os
from datetime import datetime
from urllib.parse import urlparse
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
            current_channel = {'info': line}
            
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
                'User-Agent': 'Mozilla/5.0 (compatible; M3U-Checker/1.0; +https://github.com)'
            }
            
            print(f"Attempt {attempt + 1}/{max_retries} for {url}")
            
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                is_valid, count, channels = validate_m3u_content(response.text)
                
                if is_valid:
                    return {
                        'status': 'valid',
                        'channels_count': count,
                        'channels_sample': channels[:5],  # أول 5 قنوات كعينة
                        'content': response.text,
                        'response_time': response.elapsed.total_seconds()
                    }
                else:
                    return {
                        'status': 'invalid_format',
                        'message': 'Not a valid M3U format',
                        'response_time': response.elapsed.total_seconds()
                    }
            else:
                return {
                    'status': 'http_error',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
                
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return {'status': 'timeout', 'message': 'Request timed out'}
        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                return {'status': 'connection_error', 'message': 'Connection failed'}
        except Exception as e:
            if attempt == max_retries - 1:
                return {'status': 'error', 'message': str(e)}
        
        time.sleep(1)  # انتظار قبل إعادة المحاولة
    
    return {'status': 'failed', 'message': 'All attempts failed'}

def merge_playlists(playlists_data):
    """دمج قوائم التشغيل مع إزالة التكرارات"""
    merged_header = "#EXTM3U"
    merged_channels = []
    seen_urls = set()
    
    for playlist in playlists_data:
        if playlist['status'] == 'valid' and 'content' in playlist:
            lines = playlist['content'].strip().split('\n')
            
            if lines and lines[0].startswith('#EXTM3U'):
                i = 1  # تخطي الهيدر
                while i < len(lines):
                    if lines[i].startswith('#EXTINF'):
                        # هذا سطر معلومات القناة
                        info_line = lines[i]
                        
                        # البحث عن رابط القناة التالي
                        if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith('#'):
                            channel_url = lines[i + 1].strip()
                            
                            # التحقق من عدم التكرار
                            if channel_url not in seen_urls:
                                seen_urls.add(channel_url)
                                merged_channels.append(info_line)
                                merged_channels.append(channel_url)
                            
                            i += 2  # تخطي سطرين
                        else:
                            i += 1
                    else:
                        i += 1
    
    # إضافة عدد القنوات في التعليق
    comment = f"\n# Generated: {datetime.utcnow().isoformat()}Z\n"
    comment += f"# Total Channels: {len(seen_urls)}\n"
    comment += "# Sources: " + ", ".join([p['url'] for p in playlists_data if p['status'] == 'valid'])
    
    return merged_header + comment + '\n' + '\n'.join(merged_channels)

def main():
    # الحصول على الروابط من environment variable أو command line
    if len(sys.argv) > 1:
        urls_input = sys.argv[1]
    else:
        urls_input = os.getenv('PLAYLIST_URLS', '')
    
    if not urls_input:
        print("❌ No URLs provided")
        sys.exit(1)
    
    # تحليل الروابط (يمكن أن تكون مفصولة بفواصل أو مسافات)
    urls = []
    for part in urls_input.replace(',', ' ').split():
        url = part.strip()
        if url and url.startswith('http'):
            urls.append(url)
    
    if not urls:
        print("❌ No valid URLs found")
        sys.exit(1)
    
    print(f"🔍 Checking {len(urls)} M3U playlist(s)")
    print("=" * 60)
    
    results = []
    valid_playlists = []
    
    for url in urls:
        print(f"\nChecking: {url[:60]}...")
        result = check_m3u_url(url)
        result['url'] = url
        
        results.append(result)
        
        if result['status'] == 'valid':
            print(f"✅ VALID - {result['channels_count']} channels")
            valid_playlists.append(result)
        else:
            print(f"❌ {result['status'].upper()}: {result.get('message', '')}")
    
    # دمج القوائم الصالحة
    if valid_playlists:
        merged_content = merge_playlists(valid_playlists)
        
        # حفظ الملف المدمج
        with open('merged_channels.m3u', 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        # حساب الإحصائيات
        stats = {
            'total_urls': len(urls),
            'working_urls': len(valid_playlists),
            'total_channels': sum(p['channels_count'] for p in valid_playlists),
            'unique_channels': len(set(
                url for p in valid_playlists 
                for url in [c['url'] for c in p.get('channels_sample', []) if 'url' in c]
            ))
        }
        
        # حفظ النتائج كـ JSON
        output_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'stats': stats,
            'playlists': results,
            'success': True
        }
        
        with open('check_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ SUCCESS: Merged {len(valid_playlists)} playlists")
        print(f"📊 Statistics: {stats}")
        
        # إخراج النتائج لـ GitHub Actions
        print(f"::set-output name=stats::{json.dumps(stats)}")
        print(f"::set-output name=merged_file::merged_channels.m3u")
        
    else:
        print("\n❌ FAILED: No valid playlists found")
        
        output_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'success': False,
            'playlists': results
        }
        
        with open('check_results.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
