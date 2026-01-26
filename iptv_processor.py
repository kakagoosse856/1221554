import requests
import json
import os
import re
from collections import defaultdict
from datetime import datetime
import pytz
import threading
import logging

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class M3UCollector:
    def __init__(self, country="Arabic", base_dir="LiveTV", check_links=True):
        self.channels = defaultdict(list)
        self.default_logo = "https://buddytv.netlify.app/img/no-logo.png"
        self.seen_urls = set()
        self.url_status_cache = {}
        self.output_dir = os.path.join(base_dir, country)
        self.lock = threading.Lock()
        self.check_links = check_links
        os.makedirs(self.output_dir, exist_ok=True)

    # --- تحديد نوع القناة تلقائيًا ---
    def detect_group(self, name):
        name_lower = name.lower()
        if any(k in name_lower for k in ["bein"]):
            return "Sports"
        elif any(k in name_lower for k in ["movie", "cinema", "film"]):
            return "Movies"
        elif any(k in name_lower for k in ["kids", "cartoon", "disney", "nick"]):
            return "Kids"
        elif any(k in name_lower for k in ["news", "cnn", "bbc", "aljazeera"]):
            return "News"
        elif any(k in name_lower for k in ["music", "mtv", "vh1"]):
            return "Music"
        else:
            return "Other"

    # --- التحقق من أن الرابط يعمل ---
    def check_link_active(self, url, timeout=5):
        headers = {'User-Agent': 'Mozilla/5.0'}
        with self.lock:
            if url in self.url_status_cache:
                return self.url_status_cache[url]

        try:
            # HEAD request أسرع
            r = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            if r.status_code < 400:
                with self.lock:
                    self.url_status_cache[url] = True
                return True
        except requests.RequestException:
            try:
                r = requests.get(url, timeout=timeout, headers=headers, stream=True)
                if r.status_code < 400:
                    with self.lock:
                        self.url_status_cache[url] = True
                    return True
            except:
                pass
        with self.lock:
            self.url_status_cache[url] = False
        return False

    # --- تحميل وتحويل روابط M3U ---
    def fetch_content(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r = requests.get(url, stream=True, headers=headers, timeout=10)
            r.raise_for_status()
            lines = [line.decode('utf-8', errors='ignore') if isinstance(line, bytes) else line for line in r.iter_lines()]
            return lines
        except:
            logging.warning(f"Failed to fetch {url}")
            return []

    # --- تحليل M3U ---
    def parse_and_store(self, lines, source_url):
        current_channel = {}
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                match_logo = re.search(r'tvg-logo="([^"]*)"', line)
                logo = match_logo.group(1) if match_logo else self.default_logo
                match_group = re.search(r'group-title="([^"]*)"', line)
                name_match = re.search(r',(.+)$', line)
                name = name_match.group(1).strip() if name_match else "Unnamed Channel"
                group = match_group.group(1) if match_group else self.detect_group(name)
                current_channel = {
                    'name': name,
                    'logo': logo,
                    'group': group,
                    'source': source_url
                }
            elif line.startswith('http') and current_channel:
                # تحويل الروابط إلى m3u8
                if not line.endswith(".m3u8"):
                    line = line.split("?")[0]
                    if not line.endswith(".m3u8"):
                        line += ".m3u8"
                # فحص القناة قبل إضافتها
                if self.check_links:
                    if not self.check_link_active(line):
                        logging.info(f"⚠️ Skipping inactive channel: {current_channel['name']}")
                        current_channel = {}
                        continue
                with self.lock:
                    if line not in self.seen_urls:
                        self.seen_urls.add(line)
                        current_channel['url'] = line
                        self.channels[current_channel['group']].append(current_channel)
                current_channel = {}

    # --- تصدير M3U8 ---
    def export_m3u(self, filename="LiveTV.m3u8"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            for group, channels in self.channels.items():
                for ch in channels:
                    f.write(f'#EXTINF:-1 tvg-logo="{ch["logo"]}" group-title="{group}",{ch["name"]}\n')
                    f.write(f'{ch["url"]}\n')
        logging.info(f"Exported M3U8 to {filepath}")
        return filepath

    # --- تصدير TXT ---
    def export_txt(self, filename="b1otto.txt"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for group, channels in sorted(self.channels.items()):
                f.write(f"Group: {group}\n")
                for ch in channels:
                    f.write(f"Name: {ch['name']}\nURL: {ch['url']}\nLogo: {ch['logo']}\nSource: {ch['source']}\n")
                    f.write("-"*50+"\n")
                f.write("\n")
        logging.info(f"Exported TXT to {filepath}")
        return filepath

    # --- تصدير JSON ---
    def export_json(self, filename="b1otto.json"):
        filepath = os.path.join(self.output_dir, filename)
        mumbai_tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(mumbai_tz).strftime('%Y-%m-%d %H:%M:%S')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"date": current_time, "channels": dict(self.channels)}, f, ensure_ascii=False, indent=2)
        logging.info(f"Exported JSON to {filepath}")
        return filepath

    # --- المعالجة الكاملة ---
    def process_sources(self, source_urls):
        self.channels.clear()
        self.seen_urls.clear()
        for url in source_urls:
            lines = self.fetch_content(url)
            if lines:
                self.parse_and_store(lines, url)

# --- التشغيل الرئيسي ---
def main():
    source_urls = [
        "https://raw.githubusercontent.com/Ghassanjab/Iptv-list/refs/heads/main/04_gh3.m3u.m3u",
        "https://raw.githubusercontent.com/Ghassanjab/Iptv-list/refs/heads/main/cf_wizx_cloud_001a79b5f988_Unbekannt.m3u.m3u",
    ]
    collector = M3UCollector(country="Arabic", check_links=True)
    collector.process_sources(source_urls)
    collector.export_m3u("b1otto.m3u8")
    collector.export_txt("b1otto.txt")
    collector.export_json("b1otto.json")
    total_channels = sum(len(ch) for ch in collector.channels.values())
    logging.info(f"✅ Collected {total_channels} active channels grouped into {len(collector.channels)} types")

if __name__=="__main__":
    main()
