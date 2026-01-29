#!/usr/bin/env python3
"""
Generate a final M3U with resolved URLs.

- Reads ONE M3U source only (local file OR remote RAW URL)
- Does NOT search the internet for playlists
- Designed for GitHub Actions automation
"""

import argparse
import re
import os
import sys
import requests

# allow local import
sys.path.insert(0, os.path.dirname(__file__))
import resolved


def is_url_line(s: str) -> bool:
    s = s.strip()
    return s.startswith("http://") or s.startswith("https://")


def load_input_source(input_source: str, headers=None):
    """
    Load M3U from:
    - local file path
    - remote RAW URL (GitHub raw, etc.)
    """
    if input_source.startswith(("http://", "https://")):
        print(f"[info] Loading M3U from URL: {input_source}")
        r = requests.get(input_source, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text.splitlines()
    else:
        print(f"[info] Loading M3U from file: {input_source}")
        with open(input_source, "r", encoding="utf-8") as f:
            return f.read().splitlines()


def resolve_to_final_urls(url, headers=None, skip_final_check=False):
    if skip_final_check:
        loc = resolved.get_location_header(url, headers=headers)
        return [loc] if loc else [url]

    loc = resolved.get_location_header(url, headers=headers)

    if loc and loc.endswith(".m3u8"):
        r = resolved.follow_and_inspect(loc, headers=headers)
    else:
        r = resolved.follow_and_inspect(url, headers=headers)

    if r is None:
        return [url]

    final_url = r.url
    body = r.text or ""
    ct = r.headers.get("Content-Type", "")

    if (
        "mpegurl" in ct
        or "vnd.apple.mpegurl" in ct
        or final_url.endswith(".m3u8")
        or "#EXTM3U" in body[:1000]
    ):
        entries = resolved.parse_m3u8_and_resolve(body, final_url)
        return entries or [final_url]

    embedded = resolved.try_html_embedded_redirect(body, final_url)
    if embedded:
        rr = resolved.follow_and_inspect(embedded, headers=headers)
        if rr is not None:
            if (
                "m3u8" in rr.headers.get("Content-Type", "")
                or "#EXTM3U" in rr.text[:1000]
                or rr.url.endswith(".m3u8")
            ):
                entries = resolved.parse_m3u8_and_resolve(rr.text, rr.url)
                return entries or [rr.url]
            return [rr.url]

    found = re.findall(r"https?://[^\s'\"<>]+", body)
    if found:
        return found

    if loc:
        return [loc]

    return [final_url]


def generate(input_source, output_path, headers=None):
    lines = load_input_source(input_source, headers=headers)

    out_lines = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        if line.strip().startswith("#EXTINF"):
            out_lines.append(line)
            j = i + 1

            while j < n and lines[j].strip() == "":
                j += 1

            if j < n and is_url_line(lines[j]):
                url = lines[j].strip()
                print(f"[info] Resolving: {url}")
                skip_flag = getattr(generate, "skip_final_check", False)
                final_urls = resolve_to_final_urls(
                    url, headers=headers, skip_final_check=skip_flag
                )
                chosen = final_urls[0] if final_urls else url
                out_lines.append(chosen)
                i = j + 1
                continue

        out_lines.append(line)
        i += 1

    with open(output_path, "w", encoding="utf-8") as f:
        for ln in out_lines:
            f.write(ln + "\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--input",
        "-i",
        default="https://raw.githubusercontent.com/kakagoosse856/1221554/refs/heads/main/sky-uk-nz.m3u",
        help="Local M3U file OR remote RAW M3U URL",
    )
    p.add_argument("--output", "-o", default="sky-uk-nz.resolved.m3u")
    p.add_argument("--referer", help="Optional Referer header")
    p.add_argument("--user-agent", help="Optional User-Agent header")
    p.add_argument("--skip-final-check", action="store_true")

    args = p.parse_args()

    headers = resolved.DEFAULT_HEADERS.copy()
    if args.referer:
        headers["Referer"] = args.referer
    if args.user_agent:
        headers["User-Agent"] = args.user_agent

    setattr(generate, "skip_final_check", args.skip_final_check)

    generate(args.input, args.output, headers=headers)
    print(f"[done] Wrote resolved M3U -> {args.output}")


if __name__ == "__main__":
    main()
