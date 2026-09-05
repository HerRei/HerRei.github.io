"""
Tier 2: boundaries and corner cases.

Where the catalogue is most likely to go quietly wrong: the sparsest filter,
the work with no public repository, the entry with no figure, the numbers in
the index line, the sizes of the things we ship over the wire.
"""

from __future__ import annotations

import re
import unittest

from tests.test_base import BaseE2ETestCase

CATEGORIES = ("systems", "ai", "embedded", "java", "automation")


class TestTier2BoundaryCorner(BaseE2ETestCase):
    """Tier 2: the edges of the design."""

    def entries(self):
        return re.findall(
            r'<li class="entry" data-category="([^"]+)">(.*?)</li>',
            self.raw_html,
            re.S,
        )

    # -- the filter's extremes ----------------------------------------------

    def test_sparsest_and_densest_filters(self):
        counts = {c: 0 for c in CATEGORIES}
        for cats, _ in self.entries():
            for c in cats.split():
                counts[c] += 1

        for cat, n in counts.items():
            self.record_assertion(
                2, "B1", f"Filter '{cat}' is not empty", n >= 1,
                f"'{cat}' would show {n} work(s) — never a blank catalogue",
            )
        self.record_assertion(
            2, "B1", "No filter shows everything twice",
            all(n <= len(self.entries()) for n in counts.values()),
            "No category claims more works than exist",
        )
        self.record_assertion(
            2, "B1", "Every work answers at least one filter",
            all(cats.strip() for cats, _ in self.entries()),
            "No work is unreachable from the index line",
        )
        self.record_assertion(
            2, "B1", "Categories are drawn from the declared set",
            all(c in CATEGORIES for cats, _ in self.entries() for c in cats.split()),
            "No entry carries a category the index line does not offer",
        )

    def test_filter_tokens_are_whole_words(self):
        """'ai' must not match inside another token when filtering."""
        self.record_assertion(
            2, "B2", "Filtering splits on whitespace rather than substring",
            'split(/\\s+/)' in self.raw_html and ".indexOf(cat)" in self.raw_html,
            "Categories are compared as whole tokens, so 'ai' cannot match 'automation'",
        )
        self.record_assertion(
            2, "B2", "An unknown category falls back to showing everything",
            'if (!cat) cat = "all";' in self.raw_html,
            "A missing category shows the whole catalogue rather than none of it",
        )

    # -- the awkward entries -------------------------------------------------

    def test_work_without_a_public_repository(self):
        entries = self.entries()
        private = [body for _c, body in entries if "Private collection" in body]
        self.record_assertion(
            2, "B3", "The private work is still catalogued", len(private) == 1,
            "LocalSR appears in the catalogue despite having no public repository",
        )
        if private:
            body = private[0]
            self.record_assertion(
                2, "B3", "The private work is dated 'n.d.'", "n.d." in body,
                "An unknown date is given as n.d. rather than guessed",
            )
            self.record_assertion(
                2, "B3", "The private work offers no broken link",
                re.findall(r'href="([^"]+)"', body.split('class="entry-links"')[-1]) == ["localsr/"]
                and (self.project_root / "localsr" / "index.html").is_file(),
                "LocalSR links to its public showcase; its private source repository is not linked",
            )

    def test_entries_without_figures_are_still_complete(self):
        for index, (_cats, body) in enumerate(self.entries(), start=1):
            has_prose = '<div class="prose">' in body
            self.record_assertion(
                2, "B4", f"Entry {index} carries prose", has_prose,
                f"Entry {index} describes the work in sentences",
            )
        with_figures = sum(1 for _c, b in self.entries() if "<figure" in b)
        self.record_assertion(
            2, "B4", "Figures are used sparingly", 1 <= with_figures <= 4,
            f"{with_figures} of ten entries carry a figure — the page keeps its rhythm",
        )

    # -- numbers and dates ---------------------------------------------------

    def test_dates_are_plausible(self):
        dates = re.findall(r'<dd class="date">([^<]+)</dd>', self.raw_html)
        self.record_assertion(
            2, "B5", "Every work carries a date field", len(dates) == 10,
            f"{len(dates)} date fields",
        )
        months = ("January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December")
        for date in dates:
            ok = date.strip() == "n.d." or (
                date.split()[0] in months and date.split()[-1].isdigit()
            )
            self.record_assertion(
                2, "B5", f"Date well formed: {date}", ok,
                "Dates read as 'Month Year', or n.d. where unknown",
            )

    def test_tallies_are_lining_figures(self):
        self.record_assertion(
            2, "B6", "Tallies set as lining numerals",
            ".filter .tally" in self.raw_html and "lining-nums" in self.raw_html,
            "Counts in the index line align, rather than hanging like text figures",
        )

    # -- weight over the wire -------------------------------------------------

    def test_page_and_asset_weight(self):
        size = len(self.raw_html.encode("utf-8"))
        self.record_assertion(
            2, "B7", "The document stays small", size < 120_000,
            f"index.html is {size / 1024:.0f} KB",
        )
        for path in sorted(set(re.findall(r'(?:src|href)="(assets/[^"]+)"', self.raw_html))):
            exists, bytes_ = self.auditor.check_asset_exists(path)
            if not exists or path.endswith(".pdf"):
                continue
            self.record_assertion(
                2, "B7", f"Image weight reasonable: {path}", bytes_ < 400_000,
                f"{path} is {bytes_ / 1024:.0f} KB",
            )

    def test_images_declare_their_dimensions(self):
        for tag in re.findall(r"<img\b[^>]*>", self.raw_html):
            self.record_assertion(
                2, "B8", "Image reserves its space",
                "width=" in tag and "height=" in tag,
                "Intrinsic dimensions are given, so nothing jumps as it loads",
                tag[:100],
            )

    # -- typography under strain ---------------------------------------------

    def test_long_strings_cannot_break_the_layout(self):
        html = self.raw_html
        self.record_assertion(
            2, "B9", "The email address can wrap", "word-break: break-word" in html,
            "A long address breaks rather than widening the page",
        )
        self.record_assertion(
            2, "B9", "Destination names are clipped, not stretched",
            "text-overflow: ellipsis" in html,
            "A long station name cannot widen the departure panel",
        )
        self.record_assertion(
            2, "B9", "The telemetry specimen scrolls within itself",
            "overflow-x: auto" in html,
            "Its fixed-width rows scroll inside the block instead of the page",
        )
        self.record_assertion(
            2, "B9", "Grid columns may shrink below their content",
            html.count("minmax(0, 1fr)") >= 3,
            "minmax(0, 1fr) stops long words forcing the grid open",
        )

    # -- the smallest screens -------------------------------------------------

    def test_narrow_viewport_rules(self):
        css = self.auditor.css_analysis
        queries = [q["query"] for q in css.media_queries]
        self.record_assertion(
            2, "B10", "A rule exists for phones", any("30rem" in q or "48rem" in q for q in queries),
            f"Breakpoints: {queries}",
        )
        self.record_assertion(
            2, "B10", "The drop cap shrinks on a phone",
            ".lede::first-letter { font-size: 3.6em; }" in self.raw_html,
            "A five-line drop cap would swallow a narrow column",
        )
        self.record_assertion(
            2, "B10", "The section nav gives way on a phone",
            ".rh-nav { display: none; }" in self.raw_html,
            "The running head keeps the name and the chapter, drops the rest",
        )
        self.record_assertion(
            2, "B10", "The methods table becomes a list",
            ".methods thead { display: none; }" in self.raw_html,
            "A two-column table would not survive 375px intact",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
