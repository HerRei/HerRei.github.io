"""
Tier 3: combinations.

Features rarely break alone. These check the seams: filtering against
printing, provenance against the index tallies, the specimens against the
reduced-motion rules, the design tokens against the places they are used.
"""

from __future__ import annotations

import re
import unittest

from tests.test_base import BaseE2ETestCase


class TestTier3CrossFeature(BaseE2ETestCase):
    """Tier 3: where two features meet."""

    def entries(self):
        return re.findall(
            r'<li class="entry" data-category="([^"]+)">(.*?)</li>',
            self.raw_html,
            re.S,
        )

    # -- filtering × printing ------------------------------------------------

    def test_filter_state_does_not_survive_into_print(self):
        print_block = re.search(r"@media print\s*\{(.*)\}\s*</style>", self.raw_html, re.S)
        body = print_block.group(1) if print_block else ""
        self.record_assertion(
            3, "X1", "Hidden entries return on paper",
            ".entry.is-hidden" in body and "!important" in body,
            "Whatever is filtered on screen, the printed catalogue is complete",
        )
        self.record_assertion(
            3, "X1", "The index line is not printed", ".index-line" in body,
            "Controls that cannot be pressed are not printed",
        )

    # -- filtering × the specimens -------------------------------------------

    def test_hiding_an_entry_hides_its_specimen(self):
        self.record_assertion(
            3, "X2", "Hiding removes the entry from layout",
            ".entry.is-hidden { display: none; }" in self.raw_html,
            "A filtered entry takes its figures with it",
        )
        self.record_assertion(
            3, "X2", "The clock keeps time regardless of the filter",
            "setInterval(showTime, 1000)" in self.raw_html,
            "The departure panel is not driven by the filter",
        )

    # -- provenance × the index ----------------------------------------------

    def test_every_filter_yields_reachable_work(self):
        entries = self.entries()
        for cat in ("systems", "ai", "embedded", "java", "automation"):
            selected = [b for c, b in entries if cat in c.split()]
            reachable = all(
                "github.com/HerRei/" in b or "Private collection" in b for b in selected
            )
            self.record_assertion(
                3, "X3", f"Filter '{cat}' yields works with provenance", reachable,
                f"All {len(selected)} work(s) under '{cat}' state where they are kept",
            )

    # -- tokens × usage ------------------------------------------------------

    def test_declared_tokens_are_the_ones_used(self):
        css = self.auditor.css_analysis
        declared = set(css.custom_properties)
        used = set(re.findall(r"var\((--[a-z0-9-]+)", self.raw_html))
        undefined = used - declared
        self.record_assertion(
            3, "X4", "No colour is used before it is defined", not undefined,
            f"{len(used)} tokens referenced, all declared",
            f"Undefined: {sorted(undefined)}",
        )
        unused = declared - used
        self.record_assertion(
            3, "X4", "The palette carries no dead weight", len(unused) <= 3,
            f"Unused tokens: {sorted(unused)}",
        )

    # -- motion × the specimens ----------------------------------------------

    def test_reduced_motion_reaches_every_moving_part(self):
        html = self.raw_html
        self.record_assertion(
            3, "X5", "The ticker respects reduced motion",
            "if (reduceMotion) {" in html and "startTicker();" in html,
            "The telemetry specimen waits to be started",
        )
        self.record_assertion(
            3, "X5", "The oscilloscope respects reduced motion",
            "if (reduceMotion) drawStave(); else trace();" in html,
            "The trace is drawn once rather than animated",
        )
        self.record_assertion(
            3, "X5", "Entry transitions respect reduced motion",
            "animation-duration: .001ms !important" in html,
            "The settle animation is suppressed with everything else",
        )
        self.record_assertion(
            3, "X5", "The nocturne is never automatic",
            "playBtn.addEventListener" in html and "nocturne.play(" in html,
            "Audio only ever begins on a click",
        )

    # -- headings × sections --------------------------------------------------

    def test_each_section_is_named_by_its_own_heading(self):
        for section_id, heading_id in (
            ("catalogue", "catalogue-title"),
            ("methods", "methods-title"),
            ("notice", "notice-title"),
            ("correspondence", "corr-title"),
        ):
            linked = f'id="{section_id}" aria-labelledby="{heading_id}"' in self.raw_html
            present = f'id="{heading_id}"' in self.raw_html
            self.record_assertion(
                3, "X6", f"Section '{section_id}' is announced", linked and present,
                f"#{section_id} is labelled by #{heading_id}",
            )

    # -- running head × sections ---------------------------------------------

    def test_running_head_tracks_the_sections_that_exist(self):
        watched = re.findall(r'\{ id: "([a-z]+)", name: "[^"]+" \}', self.raw_html)
        self.record_assertion(
            3, "X7", "The running head watches real sections",
            all(f'id="{s}"' in self.raw_html for s in watched) and len(watched) == 4,
            f"Watched sections: {watched}",
        )
        self.record_assertion(
            3, "X7", "Section anchors all resolve",
            all(
                f'id="{href[1:]}"' in self.raw_html
                for href in re.findall(r'href="(#[a-z-]+)"', self.raw_html)
            ),
            "Every in-page link lands on an element that exists",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
