#!/usr/bin/env python3
"""
M3U Playlist Checker
Checks M3U playlists and merges them
"""

import requests
import json
import os
from datetime import datetime

def load_urls():
    """Load URLs from playlists.json or use defaults"""
    urls = []
    
    # Try to read from playlists.json
    if os.path.exists('playlists.json'):
        try:
            with open('playlists.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if 'sources' in data:
                    urls.extend(data['sources'])
                if 'backup_sources' in data:
                    urls.extend(data['backup_sources'])
                    
                urls = list(set([url for url in urls if url and isinstance(url, str)]))
                
        except Exception as e:
            print(f"Error reading playlists.json: {e}")
            urls = []
    
    # If no URLs, use defaults
    if not urls:
        urls = [
            "https://raw.githubusercontent.com/kakagoosse856/1221554/2a5d587b525902b4a5fa4e13c977136839247f43/SSULTAN.m3u",
            "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u"
        ]
        print("Using default URLs")
    
    return urls

def check_url(url):
    """Check M3U URL"""
    try:
        print(f"Checking: {url[:60]}...")
        
        headers = {'User-Agent': 'M3U-Checker/1.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            if '#EXTM3U' in content:
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
    """Extract channels from M3U content"""
    channels = []
    lines = content.split('\n')
    
    for i in range(len(lines)):
        if lines[i].startswith('#EXTINF'):
            if i + 1 < len(lines) and lines[i + 1].startswith('http'):
                channels.append(lines[i])
                channels.append(lines[i + 1])
    
    return channels

def main():
    print("=" * 60)
    print("M3U PLAYLIST CHECKER")
    print("=" * 60)
    
    urls = load_urls()
    print(f"Found {len(urls)} playlist(s) to check")
    
    results = []
    all_channels = []
    valid_count = 0
    
    for url in urls:
        result = check_url(url)
        result['url'] = url
        results.append(result)
        
        if result['status'] == 'valid':
            valid_count += 1
            print(f"   Valid ({result['channels']} channels)")
            
            if result['content']:
                channels = extract_channels(result['content'])
                all_channels.extend(channels)
        else:
            print(f"   {result['status'].title()}: {result['error']}")
    
    # Create merged file
    if all_channels:
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
        
        header = "#EXTM3U\n"
        header += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Sources: {valid_count}/{len(urls)}\n"
        header += f"# Unique Channels: {len(unique_channels)//2}\n\n"
        
        with open('merged_channels.m3u', 'w', encoding='utf-8') as f:
            f.write(header)
            f.write('\n'.join(unique_channels))
        
        print(f"\nSUCCESS: Created merged_channels.m3u")
        print(f"   Statistics:")
        print(f"   - Valid playlists: {valid_count}/{len(urls)}")
        print(f"   - Unique channels: {len(unique_channels)//2}")
    else:
        with open('merged_channels.m3u', 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n# No valid playlists found\n")
        
        print(f"\nNo valid playlists found")
    
    # Save results
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
    
    print(f"\nFiles saved:")
    print(f"   - merged_channels.m3u")
    print(f"   - check_results.json")
    print("=" * 60)
    print("Process completed successfully!")

if __name__ == "__main__":
    main()
