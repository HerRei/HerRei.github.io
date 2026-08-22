"""
Tier 4: whole journeys, taken by the people who will actually arrive here.

Each test walks one visitor from first sight to whatever they came for, and
fails if any step along the way would leave them stuck.
"""

from __future__ import annotations

import re
import unittest

from tests.test_base import BaseE2ETestCase


class TestTier4RealWorldScenarios(BaseE2ETestCase):
    """Tier 4: four visitors."""

    def entries(self):
        return re.findall(
            r'<li class="entry" data-category="([^"]+)">(.*?)</li>',
            self.raw_html,
            re.S,
        )

    def filter_to(self, cat):
        return [b for c, b in self.entries() if cat == "all" or cat in c.split()]

    # -- 1. an engineer who wants to read code --------------------------------

    def test_engineer_looking_for_source(self):
        """Arrives, filters to systems work, reaches a repository in two clicks."""
        systems = self.filter_to("systems")
        self.record_assertion(
            4, "S1", "Systems work is findable", len(systems) == 9,
            f"The systems filter yields {len(systems)} works",
        )
        repos = re.findall(r'href="(https://github\.com/HerRei/[^"]+)"', self.raw_html)
        self.record_assertion(
            4, "S1", "Repositories are reachable", len(set(repos)) >= 9,
            f"{len(set(repos))} distinct repositories linked",
        )
        self.record_assertion(
            4, "S1", "Outbound links open safely",
            all('rel="noreferrer"' in a for a in re.findall(r"<a [^>]*https://github\.com[^>]*>", self.raw_html)),
            "External links carry rel=noreferrer",
        )
        self.record_assertion(
            4, "S1", "The first work shows its output before asking for a click",
            "specimen-terminal" in self.raw_html,
            "train-tui is demonstrated in place, not only described",
        )

    # -- 2. someone hiring ----------------------------------------------------

    def test_recruiter_reading_and_printing(self):
        """Wants the CV, the biography, and a printable page."""
        self.record_assertion(
            4, "S2", "The CV is offered on the title page",
            'href="assets/lebenslauf.pdf"' in self.raw_html,
            "The curriculum vitae is one click from the top",
        )
        exists, size = self.auditor.check_asset_exists("assets/lebenslauf.pdf")
        self.record_assertion(
            4, "S2", "The CV file is really there", exists and size > 0,
            f"lebenslauf.pdf is {size / 1024:.0f} KB",
        )
        for field in ("Institution", "Field", "Previously", "Languages"):
            self.record_assertion(
                4, "S2", f"Particulars state {field}", f"<dt>{field}</dt>" in self.raw_html,
                f"The biographical notice records {field.lower()}",
            )
        self.record_assertion(
            4, "S2", "An address is given", "mailto:hermesnathanheiniger@gmail.com" in self.raw_html,
            "There is a way to reply",
        )
        self.record_assertion(
            4, "S2", "The page prints as a document", "@media print" in self.raw_html,
            "Printing yields a catalogue rather than a screenshot of one",
        )

    # -- 3. a reader on a phone, on a train ----------------------------------

    def test_reader_on_a_phone(self):
        """Narrow screen, possibly no audio, possibly reduced motion."""
        self.record_assertion(
            4, "S3", "The viewport is declared",
            'name="viewport" content="width=device-width, initial-scale=1"' in self.raw_html,
            "The page is laid out at the device's width",
        )
        self.record_assertion(
            4, "S3", "Entries stack on a narrow screen",
            ".entry { grid-template-columns: minmax(0, 1fr); gap: 1.1rem; }" in self.raw_html,
            "The wall label moves above the entry instead of squeezing beside it",
        )
        self.record_assertion(
            4, "S3", "Audio failure is handled",
            "no audio available in this browser" in self.raw_html,
            "A browser without Web Audio is told, not left with a dead button",
        )
        self.record_assertion(
            4, "S3", "Images load lazily where they are below the fold",
            'loading="lazy"' in self.raw_html or self.raw_html.count("<img") <= 1,
            "Offscreen images do not compete with the text",
        )
        self.record_assertion(
            4, "S3", "The typeface request does not block first paint",
            "display=swap" in self.raw_html,
            "Text is readable before the webfonts arrive",
        )

    # -- 4. someone using a keyboard and a screen reader ---------------------

    def test_keyboard_and_screen_reader(self):
        """No mouse. Everything interactive must be reachable and announced."""
        html = self.raw_html
        self.record_assertion(
            4, "S4", "The catalogue can be skipped to",
            '<a class="skip-link" href="#catalogue">' in html,
            "The first stop is a link past the running head",
        )
        self.record_assertion(
            4, "S4", "Every control is a real button",
            "<div class=\"filter\"" not in html and html.count('<button class="filter"') == 6,
            "Filters are buttons, so they are focusable and pressable by keyboard",
        )
        self.record_assertion(
            4, "S4", "Decorative marks are hidden from announcement",
            html.count('aria-hidden="true"') >= 10,
            "Catalogue numerals and the colophon mark are not read aloud",
        )
        self.record_assertion(
            4, "S4", "The canvas is described",
            'aria-label="Oscilloscope tracing the synthesised tone"' in html,
            "The oscilloscope announces what it is",
        )
        self.record_assertion(
            4, "S4", "Focus is never removed without replacement",
            "outline: none" not in html and ":focus-visible" in html,
            "No rule strips the focus ring",
        )
        self.record_assertion(
            4, "S4", "The document declares its language", '<html lang="en">' in html,
            "Screen readers pronounce the page in the right language",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
