#!/usr/bin/env python3
"""Validate the static site's documents, destinations, downloads, and asset provenance."""

from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = []
        self.refs = []
        self.h1_count = 0
        self.images = []
        self.buttons = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        for attribute in ("href", "src"):
            if attribute in attrs:
                self.refs.append(attrs[attribute])
        if tag == "img":
            self.images.append(attrs)
        if tag == "button":
            self.buttons.append(attrs)


def main():
    site = Path(__file__).resolve().parents[1]
    repository = site.parent
    documents = {path.resolve(): Document(path) for path in site.rglob("*.html")}
    failures = []

    def check(condition, message):
        if not condition:
            failures.append(message)

    for path, doc in documents.items():
        check(doc.h1_count == 1, f"{path.name}: expected one main heading")
        check(all(count == 1 for count in Counter(doc.ids).values()), f"{path}: duplicate IDs")
        check(all("alt" in image and image.get("width") and image.get("height") for image in doc.images), f"{path}: missing image alternatives/dimensions")
        check(all(button.get("type") == "button" for button in doc.buttons), f"{path}: untyped buttons")
        check('<html lang="en">' in path.read_text(), f"{path}: missing language")
        for reference in doc.refs:
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                check(url.scheme in ("https", "mailto"), f"Unexpected external scheme: {reference}")
                continue
            resolved = ((repository if url.path.startswith("/") else path.parent) / unquote(url.path.lstrip("/"))).resolve() if url.path else path
            if resolved.is_dir():
                resolved = resolved / "index.html"
            check(resolved.exists(), f"{path}: missing destination {reference}")
            if url.fragment and resolved.exists() and resolved.suffix == ".html":
                target = documents.get(resolved) or Document(resolved)
                check(unquote(url.fragment) in target.ids, f"{path}: missing anchor {reference}")

    css = (site / "styles.css").read_text()
    for reference in re.findall(r'url\(["\']?([^"\')]+)', css):
        check((site / reference).is_file(), f"Missing stylesheet asset: {reference}")
    for reference in re.findall(r"['\"](assets/[^'\"]+)['\"]", (site / "showcase.js").read_text()):
        check((site / reference).is_file(), f"Missing comparison asset: {reference}")

    provenance = json.loads((site / "assets/image-provenance.json").read_text())
    for filename, expected in provenance["assets"].items():
        file = site / "assets" / filename
        check(hashlib.sha256(file.read_bytes()).hexdigest() == expected, f"Image evidence changed: {filename}")
    check(provenance["input_dimensions"] == [480, 240], "Unexpected comparison input")
    check(provenance["output_dimensions"] == [1920, 960], "Unexpected comparison result")
    check(provenance["model_id"] == "span_photo_x4", "Comparison model mismatch")
    check(not re.search(r'filter\s*:\s*blur', css), "Comparison must not add synthetic blur")
    check('@media(prefers-reduced-motion:reduce)' in css, "Missing reduced-motion support")

    release = json.loads((site / "release.json").read_text())
    check({p["id"] for p in release["platforms"]} == {"macos", "windows", "linux"}, "Incomplete platform selection")
    for platform in release["platforms"]:
        check(re.fullmatch(r"[a-f0-9]{64}", platform["sha256"]), "Invalid release checksum")
        check(release["version"] in platform["filename"], "Installer version mismatch")
        check(platform["size_bytes"] > 0, "Missing installer size")
    subprocess.run([sys.executable, str(site / "tools/sync_release.py"), "--check"], check=True)

    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Validated {len(documents)} HTML pages, all local links/assets, image provenance, accessibility structure, and release destinations")


if __name__ == "__main__":
    main()
