import requests
import os
import re
import threading
import logging

# إعدادات الـ Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IPTVExtractor:
    def __init__(self, output_folder="BottoFolder", output_file="botto.m3u"):
        self.output_folder = output_folder
        self.output_file = os.path.join(output_folder, output_file)
        self.seen_urls = set()
        self.lock = threading.Lock()
        os.makedirs(self.output_folder, exist_ok=True)
    
    # التحقق من أن الرابط نشط
    def check_link_active(self, url, timeout=5):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            if r.status_code < 400:
                return True
        except:
            try:
                r = requests.get(url, timeout=timeout, headers=headers, stream=True)
                if r.status_code < 400:
                    return True
            except:
                pass
        return False
    
    # تحميل محتوى M3U
    def fetch_lines(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r = requests.get(url, stream=True, headers=headers, timeout=10)
            r.raise_for_status()
            lines = [line.decode('utf-8', errors='ignore') if isinstance(line, bytes) else line for line in r.iter_lines()]
            logging.info(f"Fetched {len(lines)} lines from {url}")
            return lines
        except:
            logging.warning(f"Failed to fetch {url}")
            return []
    
    # استخراج وحفظ القنوات النشطة
    def process_urls(self, urls, keyword="bein"):
        all_channels = []
        for url in urls:
            lines = self.fetch_lines(url)
            current_channel = {}
            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    match_name = re.search(r',(.+)$', line)
                    name = match_name.group(1).strip() if match_name else "Unnamed"
                    current_channel['name'] = name
                    current_channel['info'] = line
                elif line.startswith("http") and current_channel:
                    if keyword.lower() in current_channel['name'].lower():
                        if line not in self.seen_urls and self.check_link_active(line):
                            with self.lock:
                                self.seen_urls.add(line)
                                all_channels.append(f"{current_channel['info']}\n{line}")
                    current_channel = {}
        
        # حفظ ملف botto.m3u
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for ch in all_channels:
                f.write(ch + "\n")
        logging.info(f"✅ Saved {len(all_channels)} active channels to {self.output_file}")

# --- التشغيل ---
if __name__ == "__main__":
    urls = [
        "https://raw.githubusercontent.com/Khz2025/Iptv/refs/heads/main/Sup%D8%A8%D9%83%D9%88%D8%B1.m3u",
        "https://raw.githubusercontent.com/Khz2025/Iptv/refs/heads/main/Sup%D8%AE%D9%84%D9%8A%D9%84.m3u",
        "https://raw.githubusercontent.com/Khz2025/Iptv/refs/heads/main/http_sup-4k_org_80_bitis-May_31_2026_6_23_pm_all_channels.m3u",
        "https://raw.githubusercontent.com/Khz2025/Iptv/refs/heads/main/%D8%A5%D8%B4%D8%AA%D8%B1%D8%A7%D9%83%20%D8%AE%D9%84%D9%8A%D9%84%20%D8%A7%D9%84%D9%83%D9%86%D9%82%20%D9%84%D9%88%D8%AD%D8%AF%D9%87.m3u8"
    ]
    
    extractor = IPTVExtractor(output_folder="BottoFolder", output_file="botto.m3u")
    extractor.process_urls(urls, keyword="bein")  # فقط قنوات بين سبورت
