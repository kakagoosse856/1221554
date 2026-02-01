import requests
import os
import sys
from datetime import datetime
import argparse

# إعدادات GitHub
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # احصل على token من GitHub Settings > Developer Settings > Personal Access Tokens
GITHUB_USERNAME = "YOUR_USERNAME"
GITHUB_REPO = "YOUR_REPO_NAME"
GITHUB_FILE = "bein_channels.m3u"

def check_m3u_url(url):
    """فحص رابط M3U"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            # التحقق من أن الملف يحتوي على صيغة M3U صحيحة
            if "#EXTM3U" in content[:20]:
                # حساب عدد القنوات
                channels = [line for line in content.split('\n') if line.startswith('#EXTINF')]
                return True, len(channels), content
            else:
                return False, 0, "Not a valid M3U file"
        else:
            return False, 0, f"HTTP Error: {response.status_code}"
            
    except Exception as e:
        return False, 0, str(e)

def update_github_file(content, commit_message="Updated M3U file"):
    """رفع الملف المحدث إلى GitHub"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE}"
        
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # الحصول على معلومات الملف الحالي (إن وجد)
        response = requests.get(url, headers=headers)
        
        sha = None
        if response.status_code == 200:
            sha = response.json()['sha']
        
        # إعداد البيانات للرفع
        data = {
            "message": commit_message,
            "content": content.encode('utf-8').hex(),
            "committer": {
                "name": "M3U Checker Bot",
                "email": "bot@example.com"
            }
        }
        
        if sha:
            data["sha"] = sha
        
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return True, "File updated successfully"
        else:
            return False, f"Failed to update: {response.json()}"
            
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='Check M3U URLs and update GitHub file')
    parser.add_argument('urls', nargs='+', help='M3U URLs to check')
    parser.add_argument('--github', action='store_true', help='Upload to GitHub')
    
    args = parser.parse_args()
    
    working_urls = []
    all_content = ["#EXTM3U"]
    
    print("=" * 60)
    print("M3U URL Checker")
    print("=" * 60)
    
    for url in args.urls:
        print(f"\nChecking: {url}")
        is_valid, channel_count, content_or_error = check_m3u_url(url)
        
        if is_valid:
            print(f"✓ VALID - {channel_count} channels found")
            working_urls.append(url)
            
            # استخراج القنوات من المحتوى وإضافتها
            lines = content_or_error.split('\n')
            for i in range(len(lines)):
                if lines[i].startswith('#EXTINF'):
                    # إضافة القناة والرابط
                    all_content.append(lines[i])  # معلومات القناة
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        all_content.append(lines[i + 1])  # رابط القناة
        else:
            print(f"✗ INVALID - {content_or_error}")
    
    if working_urls:
        final_content = '\n'.join(all_content)
        print(f"\n✓ Found {len(working_urls)} valid M3U URLs")
        print(f"✓ Total channels collected: {len([x for x in all_content if x.startswith('#EXTINF')])}")
        
        # حفظ محلي
        with open('bein_channels.m3u', 'w', encoding='utf-8') as f:
            f.write(final_content)
        print("✓ Saved locally as 'bein_channels.m3u'")
        
        # رفع إلى GitHub
        if args.github and GITHUB_TOKEN != "YOUR_GITHUB_TOKEN":
            print("\nUploading to GitHub...")
            success, message = update_github_file(
                final_content,
                f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} - {len(working_urls)} sources"
            )
            if success:
                print(f"✓ Uploaded to GitHub: {GITHUB_FILE}")
            else:
                print(f"✗ GitHub upload failed: {message}")
    else:
        print("\n✗ No valid M3U URLs found")

if __name__ == "__main__":
    main()
