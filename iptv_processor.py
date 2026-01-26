import requests
import json
import os
import re
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime
import pytz
import concurrent.futures
import threading
import logging
from bs4 import BeautifulSoup
import streamlink
import traceback

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IPTVProcessor:
    def __init__(self, country="Arabic", base_dir="LiveTV", check_links=True):
        # Collector
        self.channels = defaultdict(list)
        self.default_logo = "https://buddytv.netlify.app/img/no-logo.png"
        self.seen_urls = set()
        self.url_status_cache = {}
        self.output_dir = os.path.join(base_dir, country)
        self.lock = threading.Lock()
        self.check_links = check_links
        os.makedirs(self.output_dir, exist_ok=True)

        # Filter folders
        self.master_folder = os.path.join(self.output_dir, "master")
        self.best_folder = os.path.join(self.output_dir, "best")
        os.makedirs(self.master_folder, exist_ok=True)
        os.makedirs(self.best_folder, exist_ok=True)

    # ---------------- Collector Methods ---------------- #
    def fetch_content(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            with requests.get(url, stream=True, headers=headers, timeout=10) as response:
                response.raise_for_status()
                lines = [line.decode('utf-8', errors='ignore') if isinstance(line, bytes) else line for line in response.iter_lines()]
                logging.info(f"Fetched {len(lines)} lines from {url}")
                return '\n'.join(lines), lines
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {url}: {e}")
            return None, []

    def extract_stream_urls_from_html(self, html_content, base_url):
        if not html_content:
            return []
        soup = BeautifulSoup(html_content, 'html.parser')
        stream_urls = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            parsed_base = urlparse(base_url)
            parsed_href = urlparse(href)
            if not parsed_href.scheme:
                href = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"
            if (href.endswith(('.m3u', '.m3u8')) or 'playlist' in href.lower() or 'stream' in href.lower()) \
               and not any(exclude in href.lower() for exclude in ['telegram', '.html', '.php', 'github.com', 'login', 'signup']):
                stream_urls.add(href)
        logging.info(f"Extracted {len(stream_urls)} URLs from {base_url}")
        return list(stream_urls)

    def check_link_active(self, url, timeout=2):
        headers = {'User-Agent': 'Mozilla/5.0'}
        with self.lock:
            if url in self.url_status_cache:
                return self.url_status_cache[url]
        try:
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            if response.status_code < 400:
                with self.lock:
                    self.url_status_cache[url] = (True, url)
                return True, url
        except:
            try:
                with requests.get(url, stream=True, timeout=timeout, headers=headers) as r:
                    if r.status_code < 400:
                        with self.lock:
                            self.url_status_cache[url] = (True, url)
                        return True, url
            except:
                alt_url = url.replace('http://','https://') if url.startswith('http://') else url.replace('https://','http://')
                try:
                    response = requests.head(alt_url, timeout=timeout, headers=headers, allow_redirects=True)
                    if response.status_code < 400:
                        with self.lock:
                            self.url_status_cache[url] = (True, alt_url)
                        return True, alt_url
                except:
                    pass
            with self.lock:
                self.url_status_cache[url] = (False, url)
            return False, url

    def parse_and_store(self, lines, source_url):
        current_channel = {}
        count = 0
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                logo = re.search(r'tvg-logo="([^"]*)"', line)
                logo = logo.group(1) if logo else self.default_logo
                group = re.search(r'group-title="([^"]*)"', line)
                group = group.group(1) if group else "Uncategorized"
                name = re.search(r',(.+)$', line)
                name = name.group(1).strip() if name else "Unnamed"
                current_channel = {'name': name, 'logo': logo, 'group': group, 'source': source_url}
            elif line.startswith('http') and current_channel:
                with self.lock:
                    if line not in self.seen_urls:
                        self.seen_urls.add(line)
                        current_channel['url'] = line
                        self.channels[current_channel['group']].append(current_channel)
                        count += 1
                current_channel = {}
        logging.info(f"Parsed {count} channels from {source_url}")

    def filter_active_channels(self):
        if not self.check_links:
            logging.info("Skipping link checking for speed")
            return
        active_channels = defaultdict(list)
        all_channels = [(group, ch) for group, chans in self.channels.items() for ch in chans]
        url_set = set()
        logging.info(f"Checking {len(all_channels)} channels for activity")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_channel = {
                executor.submit(self.check_link_active, ch['url']): (group, ch)
                for group, ch in all_channels if ch['url'] not in url_set and not url_set.add(ch['url'])
            }
            for future in concurrent.futures.as_completed(future_to_channel):
                group, channel = future_to_channel[future]
                try:
                    active, updated_url = future.result()
                    if active:
                        channel['url'] = updated_url
                        active_channels[group].append(channel)
                except Exception as e:
                    logging.error(f"Error checking {channel['url']}: {e}")
        self.channels = active_channels
        logging.info(f"Active channels after filtering: {sum(len(ch) for ch in active_channels.values())}")

    def process_sources(self, source_urls):
        self.channels.clear()
        self.seen_urls.clear()
        self.url_status_cache.clear()
        all_m3u_urls = set()
        for url in source_urls:
            html_content, lines = self.fetch_content(url)
            if url.endswith('.html'):
                m3u_urls = self.extract_stream_urls_from_html(html_content, url)
                all_m3u_urls.update(m3u_urls)
            else:
                self.parse_and_store(lines, url)
        for m3u_url in all_m3u_urls:
            _, lines = self.fetch_content(m3u_url)
            self.parse_and_store(lines, m3u_url)
        if self.channels:
            self.filter_active_channels()
        else:
            logging.warning("No channels parsed from sources")

    # ---------------- Filter Methods ---------------- #
    def info_to_text(self, stream_info, url):
        text = '#EXT-X-STREAM-INF:'
        if getattr(stream_info,'program_id',None):
            text += f'PROGRAM-ID={stream_info.program_id},'
        if getattr(stream_info,'bandwidth',None):
            text += f'BANDWIDTH={stream_info.bandwidth},'
        if getattr(stream_info,'codecs',None):
            text += 'CODECS="{}"'.format(','.join(stream_info.codecs)) + ','
        if getattr(stream_info,'resolution',None) and stream_info.resolution:
            text += f'RESOLUTION={stream_info.resolution.width}x{stream_info.resolution.height}'
        return text + "\n" + url + "\n"

    def run_filter(self):
        success_count = 0
        fail_count = 0
        for group, channels in self.channels.items():
            for ch in channels:
                url = ch['url']
                slug = re.sub(r'\W+','_',ch['name'])
                try:
                    streams = streamlink.streams(url)
                    if not streams or 'best' not in streams:
                        fail_count += 1
                        continue
                    playlists = streams['best'].multivariant.playlists
                    previous_height = 0
                    master_text = ''
                    best_text = ''
                    for playlist in playlists:
                        info = playlist.stream_info
                        uri = playlist.uri
                        if getattr(info,'video',None) != 'audio_only':
                            sub_text = self.info_to_text(info, uri)
                            if info.resolution.height > previous_height:
                                master_text = sub_text + master_text
                                best_text = sub_text
                            else:
                                master_text += sub_text
                            previous_height = info.resolution.height
                    if master_text:
                        version = getattr(streams['best'].multivariant,'version',None)
                        if version:
                            master_text = f'#EXT-X-VERSION:{version}\n' + master_text
                            best_text = f'#EXT-X-VERSION:{version}\n' + best_text
                        master_text = '#EXTM3U\n' + master_text
                        best_text = '#EXTM3U\n' + best_text
                        with open(os.path.join(self.master_folder, slug + ".m3u8"), 'w+') as f:
                            f.write(master_text)
                        with open(os.path.join(self.best_folder, slug + ".m3u8"), 'w+') as f:
                            f.write(best_text)
                        success_count += 1
                    else:
                        fail_count +=1
                except Exception as e:
                    logging.warning(f"Filter failed for {slug}: {e}")
                    fail_count += 1
        logging.info(f"Filter summary: Success {success_count}, Failed {fail_count}")

    # ---------------- Export Methods ---------------- #
    def export_m3u(self, filename="LiveTV.m3u"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            for group, channels in self.channels.items():
                for ch in channels:
                    f.write(f'#EXTINF:-1 tvg-logo="{ch["logo"]}" group-title="{group}",{ch["name"]}\n')
                    f.write(f'{ch["url"]}\n')
        return filepath

    def export_json(self, filename="LiveTV.json"):
        filepath = os.path.join(self.output_dir, filename)
        now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"date": now, "channels": dict(self.channels)}, f, ensure_ascii=False, indent=2)
        return filepath

    def export_txt(self, filename="LiveTV.txt"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for group, channels in self.channels.items():
                f.write(f"Group: {group}\n")
                for ch in channels:
                    f.write(f"Name: {ch['name']}\nURL: {ch['url']}\nLogo: {ch['logo']}\nSource: {ch['source']}\n{'-'*50}\n")
                f.write("\n")
        return filepath

# ---------------- Main ---------------- #
def main():
    sources = [
        "https://raw.githubusercontent.com/ARAB-IPTV/ARAB-IPTV/main/ARABIPTV.m3u",
        "https://iptv-org.github.io/iptv/languages/ara.m3u",
    ]
    processor = IPTVProcessor(check_links=True)
    processor.process_sources(sources)
    processor.export_m3u()
    processor.export_json()
    processor.export_txt()
    processor.run_filter()
    total = sum(len(ch) for ch in processor.channels.values())
    logging.info(f"Collected {total} channels successfully!")

if __name__ == "__main__":
    main()
