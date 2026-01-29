#!/usr/bin/env python3
"""Generate a final M3U with resolved URLs using resolved.py helpers.

Usage:
    python generate_final_m3u.py --input sky-uk-nz.m3u --output sky-uk-nz.resolved.m3u

Requires `requests` (same as resolved.py).
"""
import argparse
import re
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import resolved


def is_url_line(s):
    s = s.strip()
    return s.startswith('http://') or s.startswith('https://')


def resolve_to_final_urls(url, headers=None, skip_final_check=False):
    if skip_final_check:
        loc = resolved.get_location_header(url, headers=headers)
        return [loc] if loc else [url]

    loc = resolved.get_location_header(url, headers=headers)
    if loc and loc.endswith('.m3u8'):
        r = resolved.follow_and_inspect(loc, headers=headers)
    else:
        r = resolved.follow_and_inspect(url, headers=headers)

    if r is None:
        return [url]

    final_url = r.url
    body = r.text or ''
    ct = r.headers.get('Content-Type', '')

    if 'mpegurl' in ct or 'vnd.apple.mpegurl' in ct or final_url.endswith('.m3u8') or '#EXTM3U' in body[:1000]:
        entries = resolved.parse_m3u8_and_resolve(body, final_url)
        return entries or [final_url]

    embedded = resolved.try_html_embedded_redirect(body, final_url)
    if embedded:
        rr = resolved.follow_and_inspect(embedded, headers=headers)
        if rr is not None:
            if 'm3u8' in rr.headers.get('Content-Type', '') or '#EXTM3U' in rr.text[:1000] or rr.url.endswith('.m3u8'):
                entries = resolved.parse_m3u8_and_resolve(rr.text, rr.url)
                return entries or [rr.url]
            return [rr.url]

    found = re.findall(r'https?://[^\s\'\"<>]+', body)
    if found:
        return f
