#!/usr/bin/env python3
"""Render public download links/checksums from release.json; --check is read-only."""

import argparse
import html
import json
from pathlib import Path
import re


def render_downloads(release):
    rows = []
    for platform in release["platforms"]:
        values = {key: html.escape(str(value), quote=True) for key, value in platform.items()}
        url = f'https://github.com/{release["repository"]}/releases/download/{release["version"]}/{platform["filename"]}'
        size = round(platform["size_bytes"] / 1_000_000)
        rows.append(
            f'            <article class="download-row" aria-labelledby="download-{values["id"]}">\n'
            f'              <div><h3 id="download-{values["id"]}">{values["name"]}</h3>'
            f'<p class="platform-detail">{values["requirements"]}</p>'
            f'<span class="platform-size micro">{values["backend"]} · {size} MB</span></div>\n'
            f'              <a class="download-link" data-download="{values["id"]}" '
            f'href="{html.escape(url, quote=True)}" '
            f'aria-label="Download LocalSR {html.escape(release["version"])} for {values["name"]}">'
            f'<span>Download {values["extension"]}</span><span aria-hidden="true">↓</span></a>\n'
            f'            </article>'
        )
    return "\n".join(rows)


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
        render_downloads(release) + "\n", current, flags=re.S
    )
    if count != 1:
        raise SystemExit("Expected exactly one download block")
    rendered = re.sub(r'(?<=<span data-version>)[^<]+', release["version"], rendered)
    checksums = "".join(f'{p["sha256"]}  {p["filename"]}\n' for p in release["platforms"])
    checksum_path = root / "SHA256SUMS"
    if args.check:
        if rendered != current or not checksum_path.exists() or checksum_path.read_text() != checksums:
            raise SystemExit("Download HTML/checksums need syncing: run localsr/tools/sync_release.py")
        print("Download links, release version, and checksums match release.json")
    else:
        path.write_text(rendered)
        checksum_path.write_text(checksums)
        print("Updated download HTML and SHA256SUMS")


if __name__ == "__main__":
    main()
