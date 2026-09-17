#!/usr/bin/env python3
"""Render verified releases and explicit unavailable states from release.json."""

import argparse
import html
import json
from pathlib import Path
import re


def render_rows(release, *, direct):
    # One row per platform. The newest available version provides the button;
    # older available versions and pending status are folded into the row.
    merged = {}
    order = []
    for platform in release["platforms"] + release.get("archives", []):
        pid = platform["id"].split("-")[0]
        if pid not in merged:
            merged[pid] = {"current": None, "older": [], "pending": None}
            order.append(pid)
        entry = merged[pid]
        if platform.get("available"):
            if entry["current"] is None:
                entry["current"] = platform
            else:
                entry["older"].append(platform)
        else:
            entry["pending"] = platform
    rows = []
    for pid in order:
        entry = merged[pid]
        current = entry["current"]
        pending = entry["pending"]
        if current is not None:
            values = {key: html.escape(str(value), quote=True) for key, value in current.items()}
            version = current.get("version", release["version"])
            size = round(current["size_bytes"] / 1_000_000)
            href = values["download_url"] if direct else "download/"
            # A download too large for one release asset is published in parts; the button
            # then points at the download page, which explains how to join them.
            parts = current.get("parts") or []
            label = (
                f'Download {values["extension"]} · {len(parts)} parts'
                if parts
                else f'Download {values["extension"]}'
            )
            if parts and direct:
                href = "#parts"
            action = (
                f'<a class="download-link" data-download="{values["id"]}" '
                f'href="{href}" '
                f'aria-label="Download LocalSR {html.escape(version)} for {values["name"]}">'
                f'<span>{label}</span><span aria-hidden="true">↓</span></a>'
            )
            meta = f'{html.escape(version)} · {values["backend"]} · {size} MB'
            notes = []
            for older in entry["older"]:
                # An older version, or another edition of this version (such as a GPU
                # build split into parts for GitHub's asset size limit).
                o_label = html.escape(older.get("label") or older.get("version", release["version"]))
                o_size = round(older["size_bytes"] / 1_000_000)
                parts = older.get("parts") or []
                o_detail = f"{o_size:,} MB in {len(parts)} parts" if parts else f"{o_size} MB"
                if direct:
                    o_href = html.escape(older["download_url"], quote=True)
                    notes.append(
                        f'Also available: <a href="{o_href}">{o_label} ({o_detail})</a>'
                    )
                else:
                    notes.append(
                        f'Also available: {o_label} ({o_detail}) — see the download page'
                    )
            if pending is not None:
                p_version = pending.get("version", release["version"])
                notes.append(f'{p_version} is in preparation')
            detail = values["requirements"]
            if notes:
                detail += '<br>' + ' · '.join(notes)
        else:
            # No available build at all for this platform.
            values = {key: html.escape(str(value), quote=True) for key, value in (pending or {}).items()}
            action = f'<span class="platform-detail">{values.get("status", "Not yet available")}</span>'
            meta = ""
            detail = values.get("requirements", "")
        rows.append(
            f'            <article class="download-row" aria-labelledby="download-{pid}">\n'
            f'              <div><h3 id="download-{pid}">{values["name"]}</h3>'
            f'<p class="platform-detail">{detail}</p>'
            + (f'<span class="platform-size micro">{meta}</span></div>' if meta else "</div>") + '\n'
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
