import requests, json, base64
from datetime import datetime

# GitHub settings
GITHUB_TOKEN = "PUT_YOUR_GITHUB_TOKEN_HERE"
REPO_OWNER = "YOUR_GITHUB_USERNAME"
REPO_NAME = "sonyliv-m3u8-collector"

# SonyLIV API URLs
API_URLS = [
    "https://apiv2.sonyliv.com/AGL/4.7/A/ENG/WEB/IN/UNKNOWN/TRAY/EXTCOLLECTION/30188540?layout=spotlight_layout&id=30188_540",
    "https://apiv2.sonyliv.com/AGL/4.7/A/ENG/WEB/IN/UNKNOWN/TRAY/EXTCOLLECTION/3937924064?layout=portrait_layout&id=39379_24064",
]

def fetch_api(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None

def extract_assets(api_data):
    assets = []
    if not api_data:
        return assets
    for c in api_data.get("resultObj", {}).get("containers", []):
        metadata = c.get("metadata", {})
        emf = metadata.get("emfAttributes", {})
        dai_key = emf.get("dai_asset_key")
        if dai_key:
            start_time = "00:00"
            if emf.get("match_start_time"):
                try:
                    start_time = datetime.fromtimestamp(int(emf["match_start_time"])).strftime("%H:%M")
                except:
                    pass
            assets.append({
                "title": metadata.get("title", "N/A"),
                "image": emf.get("tv_background_image", ""),
                "languages": emf.get("audio_languages", "N/A"),
                "dai_key": dai_key,
                "start_time": start_time
            })
    return assets

def generate_m3u(assets):
    m3u = "#EXTM3U\n"
    for a in assets:
        m3u += f'#EXTINF:-1 tvg-id="{a["dai_key"]}" tvg-name="{a["title"]}" tvg-logo="{a["image"]}" group-title="Soccer",{a["title"]} - {a["languages"]}\n'
        m3u += f'https://dai.google.com/linear/hls/event/{a["dai_key"]}/master.m3u8\n'
    return m3u

def push_to_github(filename, content):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    sha = None
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        sha = r.json().get("sha")
    data = {
        "message": f"Update {filename} {datetime.now()}",
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha
    }
    r = requests.put(url, headers=headers, json=data)
    print(f"Pushed {filename}: {r.status_code}")

def main():
    assets = []
    for url in API_URLS:
        data = fetch_api(url)
        if data:
            assets.extend(extract_assets(data))
    if not assets:
        print("No assets found")
        return
    # Generate files
    m3u = generate_m3u(assets)
    api_json = json.dumps({"assets": assets}, indent=2)
    # Push to GitHub
    push_to_github("playlist.m3u", m3u)
    push_to_github("api.json", api_json)

if __name__ == "__main__":
    main()
