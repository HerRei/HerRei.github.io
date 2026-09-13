#!/usr/bin/env python3
"""Render verified releases and explicit unavailable states from release.json."""

import argparse
import html
import json
from pathlib import Path
import re


def render_rows(release, *, direct):
    rows = []
    for platform in release["platforms"] + release.get("archives", []):
        values = {key: html.escape(str(value), quote=True) for key, value in platform.items()}
        version = platform.get("version", release["version"])
        size = round(platform["size_bytes"] / 1_000_000) if platform.get("available") else ""
        if platform.get("available"):
            # index links lead through the interstitial page; the download page
            # carries the direct file URLs.
            href = values["download_url"] if direct else "download/"
            action = (
                f'<a class="download-link" data-download="{values["id"]}" '
                f'href="{href}" '
                f'aria-label="Download LocalSR {html.escape(version)} for {values["name"]}">'
                f'<span>Download {values["extension"]}</span><span aria-hidden="true">↓</span></a>'
            )
        else:
            action = f'<span class="platform-detail">{values["status"]}</span>'
        meta = f'{html.escape(version)} · {values["backend"]}' + (f' · {size} MB' if size else '')
        rows.append(
            f'            <article class="download-row" aria-labelledby="download-{values["id"]}">\n'
            f'              <div><h3 id="download-{values["id"]}">{values["name"]}</h3>'
            f'<p class="platform-detail">{values["requirements"]}</p>'
            f'<span class="platform-size micro">{meta}</span></div>\n'
            f'              {action}\n'
            f'            </article>'
        )
    return "\n".join(rows)


def render_downloads(release):
    return render_rows(release, direct=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    release = json.loads((root / "release.json").read_text())
    path = root / "index.html"
    current = path.read_text()
    rendered, count = re.subn(
        r'(?<=<!-- downloads:start -->\n).*?(?=            <!-- downloads:end -->)',
        render_rows(release, direct=False) + "\n", current, flags=re.S
    )
    if count != 1:
        raise SystemExit("Expected exactly one download block")
    rendered = re.sub(r'(?<=<span data-version>)[^<]+', release["version"], rendered)
    download_page = root / "download" / "index.html"
    download_current = download_page.read_text()
    download_rendered, download_count = re.subn(
        r'(?<=<!-- downloads:start -->\n).*?(?=        <!-- downloads:end -->)',
        render_rows(release, direct=True) + "\n", download_current, flags=re.S
    )
    if download_count != 1:
        raise SystemExit("Expected exactly one download block on the download page")
    artifacts = release["platforms"] + release.get("archives", []) + release.get("sources", [])
    checksums = "".join(f'{p["sha256"]}  {p["filename"]}\n' for p in artifacts if p.get("available"))
    checksum_path = root / "SHA256SUMS"
    if args.check:
        if (rendered != current or download_rendered != download_current
                or not checksum_path.exists() or checksum_path.read_text() != checksums):
            raise SystemExit("Download HTML/checksums need syncing: run localsr/tools/sync_release.py")
        print("Download availability, release versions, and checksums match release.json")
    else:
        path.write_text(rendered)
        download_page.write_text(download_rendered)
        checksum_path.write_text(checksums)
        print("Updated download HTML and SHA256SUMS")


if __name__ == "__main__":
    main()
