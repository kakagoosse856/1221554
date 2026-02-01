#!/usr/bin/env python3
"""
سكربت التشغيل التلقائي لفحص الروابط بانتظام
"""

import subprocess
import time
import schedule
from datetime import datetime

# قائمة الروابط للفحص
URLS_TO_CHECK = [
    "https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/S3.m3u8",
    # أضف روابط أخرى هنا
    # "https://example.com/playlist.m3u",
    # "https://example.com/another.m3u",
]

def run_check():
    """تشغيل فحص الروابط"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting check...")
    
    # بناء أمر التشغيل
    urls_string = ' '.join(URLS_TO_CHECK)
    command = f'python bein_m3u.py {urls_string} --github'
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except Exception as e:
        print(f"Error running script: {e}")

def main():
    print("M3U Auto Checker Started")
    print(f"Monitoring {len(URLS_TO_CHECK)} URLs")
    print("=" * 60)
    
    # جدولة الفحص كل ساعة
    schedule.every(1).hours.do(run_check)
    
    # التشغيل الفوري أول مرة
    run_check()
    
    # الحفاظ على تشغيل السكربت
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
