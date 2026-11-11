#!/usr/bin/env python3
"""Render verified releases and explicit unavailable states from release.json."""

import argparse
import html
import json
from pathlib import Path
import re


def megabytes(size_bytes):
    return f"{round(size_bytes / 1_000_000):,} MB"


def edition_detail(item):
    # Editions too large for one GitHub release file come as parts (or an installer plus engine parts).
    parts = item.get("parts") or []
    engine = item.get("engine_parts") or []
    if parts:
        return f"{megabytes(item['size_bytes'])} in {len(parts)} parts"
    if engine:
        total = item["size_bytes"] + sum(e["size_bytes"] for e in engine)
        return f"{megabytes(total)}: installer and {len(engine)} engine parts"
    return megabytes(item["size_bytes"])


def render_rows(release, *, direct):
    # One panel per platform. The newest available standard build provides the button; other
    # editions of this version (GPU builds) and older versions are listed under it.
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
    panels = []
    for pid in order:
        entry = merged[pid]
        current = entry["current"]
        pending = entry["pending"]
        source = current if current is not None else (pending or {})
        values = {key: html.escape(str(value), quote=True) for key, value in source.items()}
        name = values.get("name", pid)
        requirements = values.get("requirements", "")
        anchor = f' id="{pid}"' if direct else ""
        size_attr = f' data-size="{megabytes(current["size_bytes"])}"' if current is not None else ""
        lines = [
            f'            <article class="platform"{anchor} data-platform="{pid}"{size_attr} aria-labelledby="download-{pid}">',
            f'              <div class="platform-head"><h3 id="download-{pid}">{name}</h3><span class="yours">For this computer</span></div>',
            f'              <p class="platform-req">{requirements}</p>',
        ]
        if current is not None:
            version = html.escape(current.get("version", release["version"]))
            size = megabytes(current["size_bytes"])
            parts = current.get("parts") or []
            parts_page = "#parts" if direct else "download/#parts"
            href = parts_page if parts else values["download_url"]
            label = f'Download {values["extension"]} · {size}'
            lines.append(f'              <p>{version} · {values["backend"]}</p>')
            lines.append(
                f'              <a class="btn download-link" data-download="{values["id"]}" href="{href}" '
                f'aria-label="Download LocalSR {version} for {name}, {size}">{label}</a>'
            )
            more = []
            for older in entry["older"]:
                if not direct and older.get("version", release["version"]) != current.get("version", release["version"]):
                    continue  # Older versions are listed on the download page only.
                o_label = html.escape(older.get("label") or older.get("version", release["version"]))
                detail = edition_detail(older)
                split = older.get("parts") or older.get("engine_parts")
                o_href = parts_page if split else html.escape(older["download_url"], quote=True)
                more.append(f'<li><a href="{o_href}">{o_label}</a> · {detail}</li>')
            if pending is not None:
                more.append(f'<li>{html.escape(pending.get("version", release["version"]))} is in preparation</li>')
            if more:
                lines.append(f'              <ul class="platform-more">{"".join(more)}</ul>')
        else:
            lines.append(f'              <p>{values.get("status", "Not yet available")}</p>')
        lines.append('            </article>')
        panels.append("\n".join(lines))
    return "\n".join(panels)


def render_downloads(release):
    return render_rows(release, direct=False)


def split_editions(release):
    return [
        item for item in release["platforms"] + release.get("archives", [])
        if item.get("available") and (item.get("parts") or item.get("engine_parts"))
    ]


def render_parts(release):
    # Editions larger than one GitHub release file (2 GB): every part, and how to use it.
    blocks = []
    for item in sorted(split_editions(release), key=lambda entry: entry["name"]):
        label = html.escape(f'{item["name"]} · {item.get("label") or item["filename"]}')
        name = html.escape(item["filename"])
        rows = []
        if item.get("engine_parts"):
            rows.append((item["download_url"], item["filename"], item["size_bytes"]))
            rows += [(e["url"], e["url"].rsplit("/", 1)[-1], e["size_bytes"]) for e in item["engine_parts"]]
            count = len(item["engine_parts"])
            both = "both" if count == 2 else f"all {count}"
            how = (f'<p>Download the installer and {both} engine parts into one '
                   f'folder, keep their names, and run the installer. It checks each part\'s size and '
                   f'SHA-256 and unpacks the engine itself.</p>')
        else:
            rows += [(e["url"], e["url"].rsplit("/", 1)[-1], e["size_bytes"]) for e in item["parts"]]
            count = len(item["parts"])
            both = "both" if count == 2 else f"all {count}"
            how = (f'<p>Download {both} parts into one folder, join them, check the '
                   f'result and make it executable:</p>\n'
                   f'          <pre><code>cat {name}.part-* &gt; {name}\n'
                   f'sha256sum {name}   # compare with SHA256SUMS\n'
                   f'chmod +x {name}</code></pre>')
        links = "\n".join(
            f'            <li><a href="{html.escape(url, quote=True)}">{html.escape(file)}</a> '
            f'<span class="quiet">{size / 1_000_000:,.0f} MB</span></li>'
            for url, file, size in rows
        )
        blocks.append(
            f'        <h3>{label}</h3>\n'
            f'          {how}\n'
            f'          <ul class="parts-list">\n{links}\n          </ul>'
        )
    return "\n".join(blocks)


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
    press_page = root / "press" / "index.html"
    press_current = press_page.read_text()
    press_rendered = re.sub(r'(?<=<span data-version>)[^<]+', release["version"], press_current)
    download_page = root / "download" / "index.html"
    download_current = download_page.read_text()
    download_rendered, download_count = re.subn(
        r'(?<=<!-- downloads:start -->\n).*?(?=        <!-- downloads:end -->)',
        render_rows(release, direct=True) + "\n", download_current, flags=re.S
    )
    if download_count != 1:
        raise SystemExit("Expected exactly one download block on the download page")
    download_rendered, parts_count = re.subn(
        r'(?<=<!-- parts:start -->\n).*?(?=        <!-- parts:end -->)',
        render_parts(release) + "\n", download_rendered, flags=re.S
    )
    if parts_count != 1:
        raise SystemExit("Expected exactly one parts block on the download page")
    artifacts = release["platforms"] + release.get("archives", []) + release.get("sources", [])
    lines = []
    for p in artifacts:
        if not p.get("available"):
            continue
        lines.append(f'{p["sha256"]}  {p["filename"]}\n')
        for part in (p.get("parts") or []) + (p.get("engine_parts") or []):
            lines.append(f'{part["sha256"]}  {part["url"].rsplit("/", 1)[-1]}\n')
    checksums = "".join(lines)
    checksum_path = root / "SHA256SUMS"
    if args.check:
        if (rendered != current or download_rendered != download_current or press_rendered != press_current
                or not checksum_path.exists() or checksum_path.read_text() != checksums):
            raise SystemExit("Download HTML/checksums need syncing: run localsr/tools/sync_release.py")
        print("Download availability, release versions, and checksums match release.json")
    else:
        path.write_text(rendered)
        download_page.write_text(download_rendered)
        press_page.write_text(press_rendered)
        checksum_path.write_text(checksums)
        print("Updated download HTML and SHA256SUMS")


if __name__ == "__main__":
    main()
