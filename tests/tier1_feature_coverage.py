"""
Tier 1: Feature coverage for the catalogue raisonné build (F1 – F13).

The page is a printed-catalogue design: warm paper, iron-gall ink, one
vermillion pigment, ten works set as wall labels. These tests check the
things that would actually be wrong if they broke — structure, provenance,
honesty of the captions, accessibility, and the print sheet — rather than
restating the stylesheet back to itself.
"""

from __future__ import annotations

import re
import unittest

from tests.test_base import BaseE2ETestCase

CATEGORIES = ("all", "systems", "ai", "embedded", "java", "automation")


class TestTier1FeatureCoverage(BaseE2ETestCase):
    """Tier 1: the thirteen features the catalogue is required to have."""

    # -- helpers -------------------------------------------------------------

    def entries(self):
        """Every <li class="entry"> with its raw markup, in catalogue order."""
        return re.findall(
            r'<li class="entry" data-category="([^"]+)">(.*?)</li>',
            self.raw_html,
            re.S,
        )

    def category_counts(self):
        counts = {c: 0 for c in CATEGORIES if c != "all"}
        for cats, _ in self.entries():
            for c in cats.split():
                counts[c] = counts.get(c, 0) + 1
        return counts

    # -- F1: the paper ground ------------------------------------------------

    def test_f1_paper_ground_and_pigments(self):
        """F1: warm paper, brown-black ink, hairline rules, one vermillion."""
        css = self.auditor.css_analysis

        for var in ("--paper", "--ink", "--ink-soft", "--rule", "--vermillion"):
            self.record_assertion(
                1, "F1", f"Pigment token {var}", css.has_variable(var),
                f"{var} is defined on :root",
            )

        self.record_assertion(
            1, "F1", "Ink is brown-black, not pure black",
            (css.get_variable("--ink") or "").lower() not in ("#000", "#000000", "black"),
            "The ink token is an iron-gall brown-black rather than #000",
        )
        self.record_assertion(
            1, "F1", "Light scheme declared", "color-scheme: light" in self.raw_html,
            "color-scheme: light stops the browser forcing a dark rendering",
        )
        self.record_assertion(
            1, "F1", "Paper grain present", "feTurbulence" in self.raw_html,
            "A grain texture is generated inline rather than fetched",
        )
        self.record_assertion(
            1, "F1", "No glow shadows on text", "text-shadow" not in self.raw_html,
            "No text-shadow anywhere — this is ink on paper, not a screen",
        )

    # -- F2: typography ------------------------------------------------------

    def test_f2_typography(self):
        """F2: Bodoni Moda for display, EB Garamond for text, mono for specimens."""
        html = self.raw_html
        for family in ("Bodoni+Moda", "EB+Garamond", "JetBrains+Mono"):
            self.record_assertion(
                1, "F2", f"Typeface requested: {family}", family in html,
                f"{family.replace('+', ' ')} is loaded from the font stylesheet",
            )
        for var in ("--didone", "--serif", "--mono"):
            self.record_assertion(
                1, "F2", f"Type token {var}", self.auditor.css_analysis.has_variable(var),
                f"{var} names a stack with real fallbacks",
            )

        self.record_assertion(
            1, "F2", "Old-style figures in running text",
            "oldstyle-nums" in html,
            "Body copy uses old-style numerals, as a book would",
        )
        self.record_assertion(
            1, "F2", "Drop cap on the opening paragraph",
            ".lede::first-letter" in html,
            "The lede opens with a drop cap rather than a plain paragraph",
        )
        self.record_assertion(
            1, "F2", "Measure is bounded", "--measure" in html and "max-width: var(--measure)" in html,
            "Prose is held to a readable measure instead of the full column",
        )
        self.record_assertion(
            1, "F2", "Optical sizing driven deliberately",
            html.count('font-variation-settings: "opsz"') >= 4,
            "Bodoni's optical size axis is set per role, not left at default",
        )

    # -- F3: the catalogue ---------------------------------------------------

    def test_f3_ten_entries_as_wall_labels(self):
        """F3: ten works, each with medium, date, and where it is kept."""
        entries = self.entries()
        self.record_assertion(
            1, "F3", "Ten works catalogued", len(entries) == 10,
            f"The catalogue holds {len(entries)} entries",
        )
        self.record_assertion(
            1, "F3", "Entries are an ordered list", '<ol class="entries" id="entries">' in self.raw_html,
            "The catalogue is an <ol>, so the numbering is real to a screen reader",
        )

        for index, (_cats, body) in enumerate(entries, start=1):
            missing = [f for f in ("<dt>Medium</dt>", "<dt>Begun</dt>", "<dt>Kept</dt>") if f not in body]
            self.record_assertion(
                1, "F3", f"Entry {index} carries a full wall label", not missing,
                f"Entry {index} states medium, date and location",
                f"Missing fields: {missing}",
            )

        titles = re.findall(r"<h3>([^<]+)</h3>", self.raw_html)
        self.record_assertion(
            1, "F3", "Every entry is titled", len(titles) == 10,
            f"{len(titles)} entry titles found",
        )
        self.record_assertion(
            1, "F3", "Catalogue numbers run I to X",
            re.findall(r'<span class="cat-no" aria-hidden="true">([IVX]+)</span>', self.raw_html)
            == ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
            "Roman numerals I–X appear in order and are hidden from screen readers",
        )

    # -- F4: the index line --------------------------------------------------

    def test_f4_index_line(self):
        """F4: six filters, each tallying what it will actually show."""
        html = self.raw_html
        buttons = re.findall(
            r'<button class="filter" type="button" data-cat="(\w+)" aria-pressed="(\w+)">'
            r'([^<]+)<span class="tally">(\d+)</span>',
            html,
        )
        self.record_assertion(
            1, "F4", "Six filters offered", len(buttons) == 6,
            f"{len(buttons)} filters in the index line",
        )
        self.record_assertion(
            1, "F4", "Exactly one filter starts pressed",
            sum(1 for _, pressed, _, _ in buttons if pressed == "true") == 1,
            "'all works' is the only filter pressed on load",
        )

        counts = self.category_counts()
        for cat, _pressed, label, tally in buttons:
            expected = len(self.entries()) if cat == "all" else counts.get(cat, 0)
            self.record_assertion(
                1, "F4", f"Tally for '{label.strip()}' is honest", int(tally) == expected,
                f"{label.strip()} claims {tally}, filter yields {expected}",
                f"category={cat}",
            )

    # -- F5: provenance ------------------------------------------------------

    def test_f5_provenance_links(self):
        """F5: every work either links to its repository or says it is private."""
        for index, (_cats, body) in enumerate(self.entries(), start=1):
            kept = re.search(r'<dd class="kept">(.*?)</dd>', body, re.S)
            self.record_assertion(
                1, "F5", f"Entry {index} states where it is kept", kept is not None,
                f"Entry {index} carries a 'Kept' field",
            )
            if not kept:
                continue
            held = "github.com/HerRei/" in kept.group(1)
            private = "Private collection" in kept.group(1)
            self.record_assertion(
                1, "F5", f"Entry {index} provenance resolves", held or private,
                "Links to a repository, or is declared a private collection",
                kept.group(1).strip()[:90],
            )

        self.record_assertion(
            1, "F5", "No link to the private local-upscale repository",
            "github.com/HerRei/local-upscale" not in self.raw_html,
            "LocalSR is not linked, because that repository is not public",
        )
        self.record_assertion(
            1, "F5", "Demonstrations point at published pages",
            all(
                url.rstrip("/").split("/")[-1]
                in {
                    "train-tui", "gpt2-piano-mps-12k", "Sbb_Tracker_Sissach",
                    "PhantomHunt", "tsp_aco_gui", "google_sheets_automation", "mockup",
                }
                for url in re.findall(r'href="(https://herrei\.github\.io/[^"]+)"', self.raw_html)
            ),
            "Every demonstration link addresses a project page that exists",
        )

    # -- F6: the specimens ---------------------------------------------------

    def test_f6_specimens(self):
        """F6: three figures that run — telemetry, nocturne, departure panel."""
        html = self.raw_html
        for element_id in ("specimen-terminal", "term-toggle-btn", "term-tick-btn",
                           "term-vram", "term-loss-graph", "term-eta"):
            self.record_assertion(
                1, "F6", f"Telemetry specimen node #{element_id}", f'id="{element_id}"' in html,
                f"#{element_id} exists for the Fig. 1 specimen",
            )
        for element_id in ("oscilloscope", "play-btn", "play-status"):
            self.record_assertion(
                1, "F6", f"Nocturne node #{element_id}", f'id="{element_id}"' in html,
                f"#{element_id} exists for the Fig. 2 specimen",
            )
        for element_id in ("departure-panel", "panel-clock"):
            self.record_assertion(
                1, "F6", f"Departure panel node #{element_id}", f'id="{element_id}"' in html,
                f"#{element_id} exists for the Fig. 3 specimen",
            )

        js = self.auditor.js_analysis
        self.record_assertion(
            1, "F6", "Nocturne uses the Web Audio API", js.has_webaudio and js.has_oscillator,
            "Tone is synthesised, not fetched as an audio file",
        )
        self.record_assertion(
            1, "F6", "Oscilloscope reads the analyser", js.has_analyser_node and js.has_canvas_2d,
            "The trace is drawn from real analyser data on a 2D canvas",
        )
        self.record_assertion(
            1, "F6", "Canvas sized to its box at device pixel ratio",
            "devicePixelRatio" in html and "setTransform" in html,
            "The backing store matches the element, so the trace is not squashed",
        )

    # -- F7: honesty ---------------------------------------------------------

    def test_f7_captions_do_not_overclaim(self):
        """F7: the figures say what they are, and the colophon says how dates were set."""
        html = self.raw_html
        self.record_assertion(
            1, "F7", "Telemetry figure admits invented numbers",
            "invented numbers" in html,
            "Fig. 1 does not pretend to be a live GPU",
        )
        self.record_assertion(
            1, "F7", "Nocturne figure credits its author",
            "Written by hand rather than by the model" in html,
            "Fig. 2 is not passed off as the model's output",
        )
        self.record_assertion(
            1, "F7", "Panel figure is marked a redrawing",
            "not a photograph of it" in html,
            "Fig. 3 is not passed off as a photograph of the hardware",
        )
        self.record_assertion(
            1, "F7", "Colophon explains the dates",
            "first appeared publicly" in html,
            "Dates are attributed to the repositories, not invented",
        )
        self.record_assertion(
            1, "F7", "Colophon explains the numbering",
            "rather than chronology" in html,
            "The arrangement is declared as the author's, not chronological",
        )
        self.record_assertion(
            1, "F7", "No unphotographed work claims a photograph",
            "photographed at home" not in html,
            "The mislabelled hardware photograph is gone",
        )

    # -- F8: accessibility ---------------------------------------------------

    def test_f8_accessibility(self):
        """F8: one h1, ordered headings, a skip link, labelled sections, visible focus."""
        html = self.raw_html
        levels = [int(n) for n in re.findall(r"<h([1-6])[^>]*>", html)]
        self.record_assertion(
            1, "F8", "Exactly one h1", levels.count(1) == 1,
            f"The document has {levels.count(1)} first-level heading(s)",
        )
        skips = [(a, b) for a, b in zip(levels, levels[1:]) if b > a + 1]
        self.record_assertion(
            1, "F8", "No skipped heading levels", not skips,
            "Heading levels descend one at a time",
            f"Skips: {skips}",
        )
        self.record_assertion(
            1, "F8", "Skip link present", 'class="skip-link"' in html,
            "Keyboard users can jump straight to the catalogue",
        )
        self.record_assertion(
            1, "F8", "Sections are named", html.count("aria-labelledby=") >= 4,
            "Each section is announced by its own heading",
        )
        self.record_assertion(
            1, "F8", "Focus is visible", ":focus-visible" in html,
            "Focus rings are styled rather than suppressed",
        )
        self.record_assertion(
            1, "F8", "Filters expose their state", 'aria-pressed="' in html,
            "Filter buttons report pressed state to assistive technology",
        )
        imgs = re.findall(r"<img\b[^>]*>", html)
        self.record_assertion(
            1, "F8", "Every image is described",
            all("alt=" in tag for tag in imgs), f"{len(imgs)} image(s), all carrying alt text",
        )
        self.record_assertion(
            1, "F8", "Buttons declare their type",
            all('type="button"' in tag for tag in re.findall(r"<button\b[^>]*>", html)),
            "No button can accidentally submit anything",
        )

    # -- F9: responsive ------------------------------------------------------

    def test_f9_responsive(self):
        """F9: the sheet reflows, and the gutter survives."""
        css = self.auditor.css_analysis
        widths = [q["query"] for q in css.media_queries if q["has_max_width"]]
        self.record_assertion(
            1, "F9", "Breakpoints defined", len(widths) >= 3,
            f"{len(widths)} max-width breakpoints: {widths}",
        )
        self.record_assertion(
            1, "F9", "Entries collapse to one column",
            "grid-template-columns: minmax(0, 1fr);" in self.raw_html,
            "The label column stacks above the entry on a narrow screen",
        )
        # Regression: `.section { padding: <v> 0 }` silently cancelled the
        # horizontal gutter that .sheet sets, flattening every section against
        # the viewport edge below 62rem.
        for name in ("section", "title-page"):
            block = re.search(r"\n\.%s\s*\{([^}]*)\}" % re.escape(name), self.raw_html)
            body = block.group(1) if block else ""
            self.record_assertion(
                1, "F9", f"Gutter survives .{name}",
                bool(block) and not re.search(r"\bpadding\s*:", body),
                f".{name} sets padding on one axis, leaving .sheet's gutter intact",
                body.strip()[:120],
            )

    # -- F10: the print sheet ------------------------------------------------

    def test_f10_print_sheet(self):
        """F10: it prints as a catalogue, filters and all."""
        block = re.search(r"@media print\s*\{(.*)\}\s*</style>", self.raw_html, re.S)
        self.record_assertion(
            1, "F10", "Print stylesheet present", block is not None,
            "The page carries a print sheet",
        )
        body = block.group(1) if block else ""
        self.record_assertion(
            1, "F10", "Running head withheld from print", ".running-head" in body,
            "Navigation furniture is dropped on paper",
        )
        self.record_assertion(
            1, "F10", "Filtered entries are restored on paper",
            ".entry.is-hidden" in body and "display: grid !important" in body,
            "Printing yields the whole catalogue, not the current filter",
        )
        self.record_assertion(
            1, "F10", "Link targets are printed", 'content: " (" attr(href) ")"' in body,
            "URLs are spelled out where they cannot be clicked",
        )
        self.record_assertion(
            1, "F10", "Entries are not broken across pages", "break-inside: avoid" in body,
            "A work stays on one page",
        )

    # -- F11: assets ---------------------------------------------------------

    def test_f11_assets(self):
        """F11: everything referenced exists; nothing misattributed is referenced."""
        referenced = sorted(set(re.findall(r'(?:src|href|data-img)="(assets/[^"]+)"', self.raw_html)))
        self.record_assertion(
            1, "F11", "Assets are referenced", len(referenced) >= 2,
            f"{len(referenced)} local asset(s) referenced: {referenced}",
        )
        for path in referenced:
            exists, size = self.auditor.check_asset_exists(path)
            self.record_assertion(
                1, "F11", f"Asset present: {path}", exists and size > 0,
                f"{path} exists ({size} bytes)",
            )
        self.record_assertion(
            1, "F11", "Portrait is the web-sized file",
            "assets/profilbild_web.jpg" in self.raw_html and "assets/profilbild.png" not in self.raw_html,
            "The 1.8 MB original is not served to visitors",
        )
        for banned, why in (
            ("IMG_1591", "the photograph is not of the hardware"),
            ("board-closeup.svg", "the cartoon rendering is not the hardware"),
            ("board-installed.svg", "the cartoon rendering is not the hardware"),
        ):
            self.record_assertion(
                1, "F11", f"Withdrawn asset absent: {banned}", banned not in self.raw_html,
                f"{banned} is not published — {why}",
            )

    # -- F12: motion ---------------------------------------------------------

    def test_f12_motion_is_restrained(self):
        """F12: little moves, and what moves can be stopped."""
        html = self.raw_html
        self.record_assertion(
            1, "F12", "Reduced motion honoured", "prefers-reduced-motion" in html,
            "Animation is disabled for readers who ask for that",
        )
        self.record_assertion(
            1, "F12", "Reduced motion reaches the script", "reduceMotion" in html,
            "The ticker does not start by itself when motion is unwelcome",
        )
        self.record_assertion(
            1, "F12", "Ticker stops in a hidden tab", "visibilitychange" in html,
            "A background tab does not keep the specimen running",
        )
        self.record_assertion(
            1, "F12", "One keyframe animation at most",
            len(self.auditor.css_analysis.keyframes) <= 1,
            f"Keyframes declared: {self.auditor.css_analysis.keyframes}",
        )
        self.record_assertion(
            1, "F12", "No parallax or scroll-jacking",
            "scroll-behavior: smooth" in html and "onscroll" not in html,
            "Scrolling is the browser's, apart from smooth anchor jumps",
        )

    # -- F13: architecture ---------------------------------------------------

    def test_f13_architecture(self):
        """F13: one file, no framework, nothing fetched but the typefaces."""
        html = self.raw_html
        css = self.auditor.css_analysis

        self.record_assertion(
            1, "F13", "Stylesheet parses", not css.parse_errors,
            "Braces balance and the stylesheet is well formed",
            str(css.parse_errors),
        )
        self.record_assertion(
            1, "F13", "One inline stylesheet", html.count("<style>") == 1,
            "All styling lives in a single block",
        )
        self.record_assertion(
            1, "F13", "One inline script", html.count("<script>") == 1,
            "All behaviour lives in a single block",
        )
        self.record_assertion(
            1, "F13", "Script is not a global spill", '(function () {' in html and '"use strict"' in html,
            "Behaviour runs inside one strict-mode closure",
        )
        self.record_assertion(
            1, "F13", "No inline event attributes", not re.search(r"\son[a-z]+\s*=", html),
            "Handlers are bound in script, not sprayed through the markup",
        )
        hosts = set(re.findall(r"https?://([a-z0-9.\-]+)", html))
        allowed = {"fonts.googleapis.com", "fonts.gstatic.com", "github.com",
                   "herrei.github.io", "www.linkedin.com", "www.w3.org"}
        self.record_assertion(
            1, "F13", "No third-party runtime dependencies", hosts <= allowed,
            f"External hosts referenced: {sorted(hosts)}",
            f"Unexpected: {sorted(hosts - allowed)}",
        )
        ids = re.findall(r'\bid="([^"]+)"', html)
        self.record_assertion(
            1, "F13", "Identifiers are unique", len(ids) == len(set(ids)),
            f"{len(ids)} ids, all distinct",
            f"Duplicates: {[i for i in ids if ids.count(i) > 1]}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
