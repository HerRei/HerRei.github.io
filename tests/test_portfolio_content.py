"""Check the static portfolio's document and asset links without dependencies."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = []
        self.elements = []
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        self.elements.append((tag, attributes))
        if "id" in attributes:
            self.ids.append(attributes["id"])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attributes):
        self.handle_starttag(tag, attributes)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing tag: {tag}")
        else:
            self.stack.pop()


class TestPortfolioContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = Document((ROOT / "index.html").read_text(encoding="utf-8"))

    def test_document_is_balanced_and_ids_are_unique(self):
        self.assertEqual(self.document.errors, [])
        self.assertEqual(self.document.stack, [])
        self.assertEqual(len(self.document.ids), len(set(self.document.ids)))

    def test_local_links_and_fragments_resolve(self):
        for tag, attrs in self.document.elements:
            for attribute in ("href", "src", "srcset"):
                if attribute not in attrs:
                    continue
                references = [part.strip().split()[0] for part in attrs[attribute].split(",")] if attribute == "srcset" else [attrs[attribute]]
                for reference in references:
                    parsed = urlsplit(reference)
                    if parsed.scheme or parsed.netloc:
                        continue
                    with self.subTest(tag=tag, reference=reference):
                        target = ROOT / unquote(parsed.path.lstrip("/")) if parsed.path else ROOT / "index.html"
                        if target.is_dir():
                            target /= "index.html"
                        self.assertTrue(target.is_file(), f"Missing asset: {reference}")
                        if parsed.fragment:
                            linked = Document(target.read_text(encoding="utf-8"))
                            self.assertIn(unquote(parsed.fragment), linked.ids)

    def test_stylesheet_assets_exist(self):
        stylesheet = ROOT / "assets/portfolio/styles.css"
        for reference in re.findall(r'url\("([^\"]+)"\)', stylesheet.read_text(encoding="utf-8")):
            with self.subTest(reference=reference):
                self.assertTrue((stylesheet.parent / reference).is_file())

    def test_image_provenance_covers_existing_derivatives(self):
        provenance = ROOT / "assets/portfolio/provenance.json"
        for asset in json.loads(provenance.read_text(encoding="utf-8"))["assets"]:
            self.assertTrue(asset.get("rights") or asset.get("license"))
            for filename in asset["files"]:
                with self.subTest(filename=filename):
                    self.assertTrue((provenance.parent / filename).is_file())

    def test_images_have_alternatives_and_reserved_dimensions(self):
        for tag, attrs in self.document.elements:
            if tag == "img":
                with self.subTest(image=attrs.get("src")):
                    self.assertIn("alt", attrs)
                    self.assertGreater(int(attrs["width"]), 0)
                    self.assertGreater(int(attrs["height"]), 0)


if __name__ == "__main__":
    unittest.main()
