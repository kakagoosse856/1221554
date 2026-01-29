import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://example.com"
}

def get_location_header(url, headers=None):
    try:
        r = requests.head(url, headers=headers, allow_redirects=False, timeout=10)
        return r.headers.get('Location')
    except:
        return None

def follow_and_inspect(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r
    except:
        return None

def parse_m3u8_and_resolve(body, base_url):
    # بسيط: استخراج أي روابط m3u8 من النص
    import re
    return re.findall(r'https?://[^\s\'\"<>]+\.m3u8', body)

def try_html_embedded_redirect(body, base_url):
    import re
    m = re.search(r'window\.location\s*=\s*["\'](https?://[^"\']+)["\']', body)
    return m.group(1) if m else None
