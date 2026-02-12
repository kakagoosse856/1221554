#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vavoo_resolver.py
Script unico: dato il nome del canale, trova il link Vavoo e lo risolve in tempo reale.
"""
import sys
import requests
import json
import os
import re

with open(os.path.join(os.path.dirname(__file__), 'config/domains.json'), encoding='utf-8') as f:
    DOMAINS = json.load(f)

VAVOO_DOMAIN = DOMAINS.get("vavoo")

def getAuthSignature():
    """Funzione che replica esattamente quella dell'addon utils.py"""
    headers = {
        "user-agent": "okhttp/4.11.0",
        "accept": "application/json",
        "content-type": "application/json; charset=utf-8",
        "content-length": "1106",
        "accept-encoding": "gzip"
    }
    data = {
        "token": "tosFwQCJMS8qrW_AjLoHPQ41646J5dRNha6ZWHnijoYQQQoADQoXYSo7ki7O5-CsgN4CH0uRk6EEoJ0728ar9scCRQW3ZkbfrPfeCXW2VgopSW2FWDqPOoVYIuVPAOnXCZ5g",
        "reason": "app-blur",
        "locale": "de",
        "theme": "dark",
        "metadata": {
            "device": {
                "type": "Handset",
                "brand": "google",
                "model": "Nexus",
                "name": "21081111RG",
                "uniqueId": "d10e5d99ab665233"
            },
            "os": {
                "name": "android",
                "version": "7.1.2",
                "abis": ["arm64-v8a", "armeabi-v7a", "armeabi"],
                "host": "android"
            },
            "app": {
                "platform": "android",
                "version": "3.1.20",
                "buildId": "289515000",
                "engine": "hbc85",
                "signatures": ["6e8a975e3cbf07d5de823a760d4c2547f86c1403105020adee5de67ac510999e"],
                "installer": "app.revanced.manager.flutter"
            },
            "version": {
                "package": "tv.vavoo.app",
                "binary": "3.1.20",
                "js": "3.1.20"
            }
        },
        "appFocusTime": 0,
        "playerActive": False,
        "playDuration": 0,
        "devMode": False,
        "hasAddon": True,
        "castConnected": False,
        "package": "tv.vavoo.app",
        "version": "3.1.20",
        "process": "app",
        "firstAppStart": 1743962904623,
        "lastAppStart": 1743962904623,
        "ipLocation": "",
        "adblockEnabled": True,
        "proxy": {
            "supported": ["ss", "openvpn"],
            "engine": "ss",
            "ssVersion": 1,
            "enabled": True,
            "autoServer": True,
            "id": "pl-waw"
        },
        "iap": {
            "supported": False
        }
    }
    try:
        resp = requests.post("https://www.vavoo.tv/api/app/ping", json=data, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("addonSig")
    except Exception as e:
        print(f"Errore nel recupero della signature: {e}", file=sys.stderr)
        return None

def get_channels():
    signature = getAuthSignature()
    if not signature:
        print("[DEBUG] Failed to get signature for channels", file=sys.stderr)
        return []
    
    headers = {
        "user-agent": "okhttp/4.11.0",
        "accept": "application/json",
        "content-type": "application/json; charset=utf-8",
        "accept-encoding": "gzip",
        "mediahubmx-signature": signature
    }
    all_channels = []
    # قم بتعديل هذه المجموعات لسحب كل القنوات التي تريدها
    groups = ["Italy", "Germany", "USA", "UK", "France", "Spain", "Portugal", "Turkey", "Arabic", "International", "Sports", "Documentary", "Kids", "Music", "News", "Entertainment", "Movies", "Series"]
    
    for group in groups:
        print(f"[DEBUG] Fetching group: {group}", file=sys.stderr)
        cursor = 0
        while True:
            data = {
                "language": "de",
                "region": "AT",
                "catalogId": "iptv",
                "id": "iptv",
                "adult": False,
                "search": "",
                "sort": "name",
                "filter": {"group": group},
                "cursor": cursor,
                "clientVersion": "3.0.2"
            }
            try:
                resp = requests.post(f"https://{VAVOO_DOMAIN}/mediahubmx-catalog.json", json=data, headers=headers, timeout=10)
                resp.raise_for_status()
                r = resp.json()
                items = r.get("items", [])
                all_channels.extend(items)
                print(f"[DEBUG] Got {len(items)} channels from {group}, cursor: {cursor}", file=sys.stderr)
                cursor = r.get("nextCursor")
                if not cursor:
                    break
            except Exception as e:
                print(f"[DEBUG] Error getting channels for group {group}: {e}", file=sys.stderr)
                break
    return all_channels

def resolve_vavoo_link(link):
    signature = getAuthSignature()
    if not signature:
        print("[DEBUG] Failed to get signature for resolution", file=sys.stderr)
        return None
        
    headers = {
        "user-agent": "MediaHubMX/2",
        "accept": "application/json",
        "content-type": "application/json; charset=utf-8",
        "content-length": "115",
        "accept-encoding": "gzip",
        "mediahubmx-signature": signature
    }
    data = {
        "language": "de",
        "region": "AT",
        "url": link,
        "clientVersion": "3.0.2"
    }
    try:
        resp = requests.post(f"https://{VAVOO_DOMAIN}/mediahubmx-resolve.json", json=data, headers=headers, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list) and result and result[0].get("url"):
            return result[0]["url"]
        elif isinstance(result, dict) and result.get("url"):
            return result["url"]
        else:
            print(f"[DEBUG] Unexpected response format: {result}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"[DEBUG] Error resolving link: {e}", file=sys.stderr)
        return None

def normalize_vavoo_name(name):
    name = name.strip()
    name = re.sub(r'\s+\.[a-zA-Z]$', '', name)
    return name.upper()

def resolve_direct_link(link):
    if not "vavoo" in link:
        print("[DEBUG] Il link non sembra essere un link Vavoo", file=sys.stderr)
        return None
        
    signature = getAuthSignature()
    if not signature:
        print("[DEBUG] Failed to get signature for direct resolution", file=sys.stderr)
        return None
        
    headers = {
        "user-agent": "MediaHubMX/2",
        "accept": "application/json",
        "content-type": "application/json; charset=utf-8",
        "content-length": "115",
        "accept-encoding": "gzip",
        "mediahubmx-signature": signature
    }
    data = {
        "language": "de",
        "region": "AT",
        "url": link,
        "clientVersion": "3.0.2"
    }
    try:
        resp = requests.post(f"https://{VAVOO_DOMAIN}/mediahubmx-resolve.json", json=data, headers=headers, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        print(f"[DEBUG] Direct resolution response: {result}", file=sys.stderr)
        
        if isinstance(result, list) and result and result[0].get("url"):
            return result[0]["url"]
        elif isinstance(result, dict) and result.get("url"):
            return result["url"]
        else:
            print(f"[DEBUG] Unexpected response format in direct resolution: {result}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"[DEBUG] Error in direct resolution: {e}", file=sys.stderr)
        return None

def build_vavoo_cache(channels):
    cache = {}
    for ch in channels:
        name = ch.get("name", "").strip()
        url = ch.get("url", "")
        if not name or not url:
            continue
        cache[name] = url
    return cache

if "--build-cache" in sys.argv:
    channels = get_channels()
    cache = build_vavoo_cache(channels)
    
    # حفظ كل القنوات في ملف واحد
    with open("vavoo_cache.json", "w", encoding="utf-8") as f:
        json.dump({"links": cache, "total_channels": len(cache), "groups": list(set([ch.get('group', 'Unknown') for ch in channels]))}, f, ensure_ascii=False, indent=2)
    
    # حفظ القنوات حسب المجموعة
    os.makedirs("channels_by_group", exist_ok=True)
    groups = {}
    for ch in channels:
        group = ch.get('group', 'Unknown')
        if group not in groups:
            groups[group] = []
        groups[group].append(ch)
    
    for group, group_channels in groups.items():
        with open(f"channels_by_group/{group}.json", "w", encoding="utf-8") as f:
            json.dump(group_channels, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Cache Vavoo generata con successo!")
    print(f"📺 Totale canali: {len(cache)}")
    print(f"📁 Gruppi trovati: {len(groups)}")
    print(f"💾 Salvato in: vavoo_cache.json")
    print(f"📂 Canali per gruppo salvati in: channels_by_group/")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("=" * 60)
        print("🎬 Vavoo Resolver - استخرج روابط القنوات مباشرة")
        print("=" * 60)
        print("\n📌 الاستخدام:")
        print("  python3 vavoo_resolver.py --build-cache              # سحب كل القنوات")
        print("  python3 vavoo_resolver.py --dump-channels           # عرض كل القنوات")
        print("  python3 vavoo_resolver.py 'Rai 1'                   # بحث عن قناة وحل الرابط")
        print("  python3 vavoo_resolver.py 'Rai 1' --original-link   # رابط Vavoo الأصلي فقط")
        print("  python3 vavoo_resolver.py 'https://vavoo.to/...'    # حل رابط مباشر")
        print("\n⚙️  الإعدادات:")
        print("  config/domains.json - ملف النطاقات")
        print("\n" + "=" * 60)
        sys.exit(1)
    
    if "--dump-channels" in sys.argv:
        channels = get_channels()
        print(json.dumps(channels, indent=2, ensure_ascii=False))
        sys.exit(0)
        
    input_arg = sys.argv[1]
    return_original_link = "--original-link" in sys.argv
    
    if "vavoo.to" in input_arg and "/play/" in input_arg:
        print(f"[DEBUG] Direct Vavoo link detected: {input_arg}", file=sys.stderr)
        resolved = resolve_direct_link(input_arg)
        if resolved:
            print(resolved)
            sys.exit(0)
        else:
            print("[DEBUG] Failed to resolve direct link", file=sys.stderr)
            print("RESOLVE_FAIL", file=sys.stderr)
            sys.exit(4)
    
    wanted = normalize_vavoo_name(input_arg)
    print(f"[DEBUG] Looking for channel: {wanted}", file=sys.stderr)
    
    try:
        channels = get_channels()
        print(f"[DEBUG] Found {len(channels)} total channels", file=sys.stderr)
        
        found = None
        for ch in channels:
            chname = normalize_vavoo_name(ch.get('name', ''))
            if chname == wanted:
                found = ch
                print(f"[DEBUG] Found exact match: {ch.get('name')}", file=sys.stderr)
                break
        
        if not found:
            for ch in channels:
                original_name = ch.get('name', '').strip().upper()
                clean_name = re.sub(r'\s+\.[a-zA-Z]$', '', original_name)
                clean_name = re.sub(r'\s+(HD|FHD|4K)$', '', clean_name)
                
                if wanted in clean_name or clean_name in wanted:
                    found = ch
                    print(f"[DEBUG] Found partial match: {ch.get('name')}", file=sys.stderr)
                    break
        
        if not found:
            print(f"[DEBUG] Channel '{wanted}' not found", file=sys.stderr)
            print("NOT_FOUND", file=sys.stderr)
            sys.exit(2)
            
        url = found.get('url')
        if not url:
            print("[DEBUG] No URL found for channel", file=sys.stderr)
            print("NO_URL", file=sys.stderr)
            sys.exit(3)
            
        print(f"[DEBUG] Found Vavoo URL: {url}", file=sys.stderr)
        
        if return_original_link:
            print(url)
            sys.exit(0)
        
        print(f"[DEBUG] Resolving URL: {url}", file=sys.stderr)
        resolved = resolve_vavoo_link(url)
        if resolved:
            print(resolved)
            sys.exit(0)
        else:
            print("[DEBUG] Failed to resolve URL", file=sys.stderr)
            print("RESOLVE_FAIL", file=sys.stderr)
            sys.exit(4)
            
    except Exception as e:
        print(f"[DEBUG] Exception: {str(e)}", file=sys.stderr)
        print("ERROR", file=sys.stderr)
        sys.exit(5)
