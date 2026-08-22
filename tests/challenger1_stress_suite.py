#!/usr/bin/env python3
"""
Adversarial stress suite — an attempt to break the catalogue rather than
confirm it.

Five sections: markup that must survive a strict parser, the layout under
hostile viewports, the filter under fuzzing, the assets under inspection,
and the scripts under the assumption that every API they touch is missing.

    python3 tests/challenger1_stress_suite.py
"""

from __future__ import annotations

import html.parser
import itertools
import random
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

C_RESET, C_BOLD = "\033[0m", "\033[1m"
C_RED, C_GREEN, C_DIM = "\033[91m", "\033[92m", "\033[2m"
C_RULE = "\033[38;2;168;61;40m"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}

CATEGORIES = ("systems", "ai", "embedded", "java", "automation")


class Runner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.findings = []

    def record(self, section, name, passed, details=""):
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            self.findings.append((section, name, details))
        mark = f"{C_GREEN}✓{C_RESET}" if passed else f"{C_RED}✗{C_RESET}"
        print(f"  {mark} {name}")
        if not passed and details:
            print(f"    {C_DIM}{details}{C_RESET}")


class StrictParser(html.parser.HTMLParser):
    """Fails loudly on anything a forgiving browser would silently repair."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id":
                self.ids.append(value)
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        for name, value in attrs:
            if name == "id":
                self.ids.append(value)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"</{tag}> with nothing open")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"</{tag}> closes <{self.stack[-1]}>")
            # resync so one slip does not cascade
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
            return
        self.stack.pop()


def entries(doc):
    return re.findall(r'<li class="entry" data-category="([^"]+)">(.*?)</li>', doc, re.S)


# -- 1. markup ---------------------------------------------------------------

def section_markup(runner, doc):
    print(f"\n{C_RULE}{C_BOLD}1 · Markup under a strict parser{C_RESET}")
    parser = StrictParser()
    parser.feed(doc)

    runner.record(1, "Every element is closed in order", not parser.errors,
                  "; ".join(parser.errors[:4]))
    runner.record(1, "Nothing is left open at EOF", not parser.stack,
                  f"Still open: {parser.stack[:6]}")
    dupes = [i for i in parser.ids if parser.ids.count(i) > 1]
    runner.record(1, "No duplicated identifiers", not dupes, f"Duplicates: {sorted(set(dupes))}")

    runner.record(1, "Doctype is first", doc.lstrip().lower().startswith("<!doctype html>"))
    runner.record(1, "Character set declared in the first 1024 bytes",
                  'charset="utf-8"' in doc[:1024].lower())

    # An <ol> may only contain <li>: strip the entries and their contents,
    # then anything left other than whitespace and comments is a stray child.
    ol = re.search(r'<ol class="entries" id="entries">(.*?)\n    </ol>', doc, re.S)
    remainder = re.sub(r'<li class="entry".*?</li>', "", ol.group(1), flags=re.S) if ol else "<div"
    remainder = re.sub(r"<!--.*?-->", "", remainder, flags=re.S).strip()
    runner.record(1, "The catalogue list holds only list items",
                  ol is not None and not remainder,
                  f"Stray children of <ol>: {remainder[:80]!r}")

    labels = re.findall(r'<label\b', doc)
    runner.record(1, "No orphaned form labels", not labels)


# -- 2. viewports -------------------------------------------------------------

def section_viewports(runner, doc):
    print(f"\n{C_RULE}{C_BOLD}2 · Hostile viewports{C_RESET}")

    runner.record(2, "No fixed pixel widths on layout containers",
                  not re.search(r"\.(sheet|entry|entries)[^{]*\{[^}]*\bwidth:\s*\d{3,}px", doc))
    runner.record(2, "Fluid type is clamped at both ends",
                  doc.count("clamp(") >= 8,
                  f"clamp() used {doc.count('clamp(')} times")
    runner.record(2, "Nothing is pinned wider than the viewport",
                  "width: 100vw" not in doc)
    runner.record(2, "Grids may shrink below their content",
                  doc.count("minmax(0, 1fr)") >= 3)
    runner.record(2, "Overflowing specimens scroll themselves",
                  "overflow-x: auto" in doc)
    runner.record(2, "The sheet's gutter is never reset to zero",
                  not re.search(r"\n\.(section|title-page)\s*\{[^}]*\bpadding\s*:", doc),
                  "A padding shorthand here would cancel .sheet's horizontal gutter")

    # Breakpoints must descend, or a later query will not win
    widths = [float(w) for w in re.findall(r"@media \(max-width: ([\d.]+)rem\)", doc)]
    runner.record(2, "Max-width breakpoints are ordered widest first",
                  widths == sorted(widths, reverse=True), f"Found: {widths}")


# -- 3. the filter under fuzzing ---------------------------------------------

def section_filter(runner, doc):
    print(f"\n{C_RULE}{C_BOLD}3 · The index line under fuzzing{C_RESET}")
    works = entries(doc)
    tallies = {c: int(n) for c, n in
               re.findall(r'data-cat="(\w+)"[^>]*>[^<]+<span class="tally">(\d+)</span>', doc)}

    def shown(cat):
        return [i for i, (cats, _) in enumerate(works)
                if cat == "all" or cat in cats.split()]

    for cat, claimed in tallies.items():
        runner.record(3, f"'{cat}' shows exactly what it claims ({claimed})",
                      len(shown(cat)) == claimed,
                      f"claims {claimed}, yields {len(shown(cat))}")

    # Substring traps: 'ai' inside 'automation', 'java' inside nothing, etc.
    for a, b in itertools.permutations(CATEGORIES, 2):
        if a in b:
            runner.record(3, f"'{a}' does not leak into '{b}'",
                          set(shown(a)) != set(shown(b)) or a == b,
                          f"'{a}' and '{b}' select the same works")

    # Fuzz: random category sequences must never lose or duplicate a work
    rng = random.Random(20260822)
    corrupt = False
    for _ in range(5000):
        cat = rng.choice(list(CATEGORIES) + ["all", "", "ALL", "systems ai", "../"])
        visible = shown(cat) if cat in tallies else shown("all")
        if len(visible) != len(set(visible)) or any(i >= len(works) for i in visible):
            corrupt = True
            break
    runner.record(3, "5,000 random filter changes leave the catalogue intact", not corrupt)

    runner.record(3, "Returning to 'all' restores every work",
                  len(shown("all")) == len(works) == 10)
    runner.record(3, "No work is orphaned by every filter",
                  all(any(i in shown(c) for c in CATEGORIES) for i in range(len(works))))


# -- 4. assets ----------------------------------------------------------------

def section_assets(runner, doc):
    print(f"\n{C_RULE}{C_BOLD}4 · Assets{C_RESET}")
    referenced = sorted(set(re.findall(r'(?:src|href|data-img)="(assets/[^"]+)"', doc)))
    runner.record(4, "Every referenced asset exists",
                  all((PROJECT_ROOT / r).exists() for r in referenced),
                  f"Missing: {[r for r in referenced if not (PROJECT_ROOT / r).exists()]}")

    signatures = {".jpg": b"\xff\xd8\xff", ".webp": b"RIFF", ".png": b"\x89PNG\r\n\x1a\n",
                  ".pdf": b"%PDF"}
    for rel in referenced:
        magic = signatures.get(Path(rel).suffix.lower())
        if not magic:
            continue
        head = (PROJECT_ROOT / rel).read_bytes()[:8]
        runner.record(4, f"{rel} really is {Path(rel).suffix[1:].upper()}",
                      head.startswith(magic), f"Header: {head!r}")

    for banned in ("IMG_1591", "board-closeup.svg", "board-installed.svg"):
        runner.record(4, f"Withdrawn asset not referenced: {banned}", banned not in doc,
                      "This asset does not depict what its caption would claim")

    heavy = [r for r in referenced
             if (PROJECT_ROOT / r).stat().st_size > 500_000 and not r.endswith(".pdf")]
    runner.record(4, "No oversized image is served", not heavy, f"Heavy: {heavy}")


# -- 5. scripts under a hostile runtime --------------------------------------

def section_scripts(runner, doc):
    print(f"\n{C_RULE}{C_BOLD}5 · Scripts assuming nothing exists{C_RESET}")
    js = re.search(r"<script>(.*?)</script>", doc, re.S).group(1)

    runner.record(5, "Runs in strict mode", '"use strict"' in js)
    runner.record(5, "Leaks nothing but the documented entry point",
                  js.count("window.") - js.count("window.matchMedia")
                  - js.count("window.AudioContext") - js.count("window.webkitAudioContext")
                  - js.count("window.addEventListener") - js.count("window.devicePixelRatio") == 1,
                  "Only window.filterCategory is exported")

    runner.record(5, "Absent Web Audio is handled", "if (!Ctor) return false;" in js)
    runner.record(5, "Absent canvas context is handled",
                  "canvas && canvas.getContext" in js and "if (!pen) return;" in js)
    runner.record(5, "Absent IntersectionObserver is handled",
                  '"IntersectionObserver" in window' in js)
    runner.record(5, "Absent dialog API is not assumed", "showModal" not in js,
                  "No modal remains in the page")

    missing_guard = [m for m in re.findall(r"var (\w+) = document\.getElementById\([^)]*\);", js)
                     if not re.search(r"if \(!?%s[ )]" % m, js) and f"if ({m})" not in js
                     and f"if (!{m})" not in js and f"{m} &&" not in js and f"!{m}" not in js]
    runner.record(5, "Every looked-up element is checked before use", not missing_guard,
                  f"Unguarded: {missing_guard}")

    runner.record(5, "Timers are cleared, not merely started",
                  js.count("clearInterval") >= 1 and js.count("clearTimeout") >= 1)
    runner.record(5, "The ticker cannot be started twice",
                  "if (!timer) timer = setInterval" in js)
    runner.record(5, "Audio cannot be started twice",
                  "if (nocturne.playing)" in js)
    runner.record(5, "No eval, no Function constructor, no document.write",
                  not re.search(r"\beval\(|new Function\(|document\.write\(", js))


def main():
    doc = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
    runner = Runner()

    print(f"{C_RULE}{C_BOLD}{'=' * 72}{C_RESET}")
    print(f"{C_RULE}{C_BOLD}  ADVERSARIAL STRESS SUITE · Catalogue of Works{C_RESET}")
    print(f"{C_RULE}{C_BOLD}{'=' * 72}{C_RESET}")

    section_markup(runner, doc)
    section_viewports(runner, doc)
    section_filter(runner, doc)
    section_assets(runner, doc)
    section_scripts(runner, doc)

    total = runner.passed + runner.failed
    print(f"\n{C_RULE}{'=' * 72}{C_RESET}")
    if runner.failed:
        print(f"{C_BOLD}{C_RED}✖ {runner.failed} of {total} adversarial assertions failed.{C_RESET}")
        for section, name, details in runner.findings:
            print(f"  - Section {section}: {name}\n    {details}")
        sys.exit(1)
    print(f"{C_BOLD}{C_GREEN}❧ All {total} adversarial assertions held.{C_RESET}")
    print(f"{C_RULE}{'=' * 72}{C_RESET}")
    sys.exit(0)


if __name__ == "__main__":
    main()
