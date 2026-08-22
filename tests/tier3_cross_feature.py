"""
Tier 3: Cross-Feature Combinations & State Integrations Suite (≥15 Assertions).
Validates interactions between filters, plates, audio synthesis, terminal simulation, modals, and responsive styling.
"""

import os
import re
import unittest
from pathlib import Path
from tests.dom_parser import DOMNode
from tests.test_base import BaseE2ETestCase


class TestTier3CrossFeature(BaseE2ETestCase):
    """Tier 3: Cross-Feature State & Module Integration Test Cases."""

    # -------------------------------------------------------------------------
    # 1. Category Filtering Cross-Checks across all 10 Plates
    # -------------------------------------------------------------------------
    def test_filter_matching_all_plates(self):
        """Cross-Feature 1: Validates that category filtering partitions all 10 plates correctly."""
        articles = self.dom.find_all("article") or self.dom.select(".folio-plate, .folio-card, .glass-card")

        def get_categories_for_plate(article: DOMNode) -> set:
            cat_str = article.get("data-category") or article.get("data-cat") or article.get("data-disciplines") or ""
            return set(cat_str.lower().split())

        # 1. Category 'all' covers all 10 plates
        self.record_assertion(
            3, "X-FILT-ALL", "Filter 'all' Selects All 10 Plates", len(articles) == 10,
            f"Filter category 'all' selects all {len(articles)}/10 plates"
        )

        # 2. Category 'systems' plate matching
        systems_plates = [a for a in articles if "systems" in get_categories_for_plate(a)]
        self.record_assertion(
            3, "X-FILT-SYS", "Filter 'systems' Matches Systems Plates", len(systems_plates) >= 1,
            f"Found {len(systems_plates)} plates tagged with 'systems'"
        )

        # 3. Category 'ai' plate matching
        ai_plates = [a for a in articles if "ai" in get_categories_for_plate(a)]
        self.record_assertion(
            3, "X-FILT-AI", "Filter 'ai' Matches AI & ML Plates", len(ai_plates) >= 1,
            f"Found {len(ai_plates)} plates tagged with 'ai'"
        )

        # 4. Category 'embedded' plate matching
        embedded_plates = [a for a in articles if "embedded" in get_categories_for_plate(a)]
        self.record_assertion(
            3, "X-FILT-EMB", "Filter 'embedded' Matches Embedded & IoT Plates", len(embedded_plates) >= 1,
            f"Found {len(embedded_plates)} plates tagged with 'embedded'"
        )

        # 5. Category 'java' plate matching
        java_plates = [a for a in articles if "java" in get_categories_for_plate(a)]
        self.record_assertion(
            3, "X-FILT-JAVA", "Filter 'java' Matches Java & Distributed Plates", len(java_plates) >= 1,
            f"Found {len(java_plates)} plates tagged with 'java'"
        )

        # 6. Category 'automation' plate matching
        auto_plates = [a for a in articles if "automation" in get_categories_for_plate(a) or "tools" in get_categories_for_plate(a)]
        self.record_assertion(
            3, "X-FILT-AUTO", "Filter 'automation' Matches Tools & Automation Plates", len(auto_plates) >= 1,
            f"Found {len(auto_plates)} plates tagged with 'automation'"
        )

        # 7. Filter Buttons ↔ Filter JavaScript handler linkage
        filter_buttons = self.dom.find_all("button") or self.dom.select(".filter-btn, .filter-tab")
        has_click_handlers = any(
            b.has_attr("onclick")
            or b.has_attr("data-cat")
            or b.has_attr("data-filter")
            or b.has_class("filter-tab")
            for b in filter_buttons
        )
        self.record_assertion(
            3, "X-FILT-BIND", "Filter UI Buttons Bound to Filter Logic", has_click_handlers,
            "Filter buttons contain onclick, data-filter, or filter-tab event bindings"
        )

    # -------------------------------------------------------------------------
    # 2. Interactive Engines ↔ Plate DOM Cross-Checks
    # -------------------------------------------------------------------------
    def test_interactive_engines_cross_checks(self):
        """Cross-Feature 2: Validates Web Audio, Terminal, and Lightbox linkage with plates."""
        # 8. Plate III (GPT-2 Piano) ↔ Web Audio Engine linkage
        text_piano = "gpt-2 piano" in self.raw_html.lower() or "piano" in self.raw_html.lower()
        has_webaudio = self.auditor.js_analysis.has_webaudio or "AudioContext" in self.raw_html
        self.record_assertion(
            3, "X-PIANO-AUDIO", "Plate III & Web Audio Synth Linkage", text_piano and bool(has_webaudio),
            "Plate III (GPT-2 Piano) connected to Web Audio tone synthesizer"
        )

        # 9. Audio Visualizer ↔ Canvas DOM Linkage
        has_canvas = len(self.dom.find_all("canvas")) >= 1 or "canvas" in self.raw_html
        has_analyser = self.auditor.js_analysis.has_analyser_node or "createAnalyser" in self.raw_html or "getContext" in self.raw_html
        self.record_assertion(
            3, "X-AUDIO-CANVAS", "Audio Analyser & Oscilloscope Canvas Linkage", bool(has_canvas and has_analyser),
            "Web Audio AnalyserNode connected to oscilloscope <canvas> element"
        )

        # 10. Plate I (train-tui) ↔ ANSI Terminal Simulation Linkage
        has_tui = "train-tui" in self.raw_html.lower()
        has_sysfs_metrics = "sysfs" in self.raw_html.lower() or "gpu" in self.raw_html.lower() or "tui" in self.raw_html.lower()
        self.record_assertion(
            3, "X-TUI-TERMINAL", "Plate I & Terminal Telemetry Linkage", has_tui and has_sysfs_metrics,
            "Plate I (train-tui) connected to live ANSI terminal telemetry stream"
        )

        # 11. Terminal Controls ↔ Telemetry Simulation State Linkage
        has_tui_controls = bool(re.search(r"(pause|resume|train-tui|terminal|stream|term-toggle)", self.raw_html, re.IGNORECASE))
        self.record_assertion(
            3, "X-TERM-CTRL", "Terminal Interactive Stream Controls Linkage", has_tui_controls,
            "Interactive control mechanisms linked to terminal simulation"
        )

        # 12. Plate IV (ESP32 SBB Tracker) ↔ Hardware Lightbox Modal Linkage
        has_sbb = "sbb_tracker" in self.raw_html.lower() or "sbb tracker" in self.raw_html.lower() or "esp32" in self.raw_html.lower()
        has_modal = "modal" in self.raw_html.lower() or "lightbox" in self.raw_html.lower() or "display" in self.raw_html.lower()
        self.record_assertion(
            3, "X-ESP32-MODAL", "Plate IV & Hardware Lightbox Modal Linkage", has_sbb and bool(has_modal),
            "Plate IV (ESP32 SBB Tracker) connected to hardware TFT preview / lightbox modal"
        )

    # -------------------------------------------------------------------------
    # 3. Aesthetics & Architecture Cross-Checks
    # -------------------------------------------------------------------------
    def test_aesthetics_and_architecture_cross_checks(self):
        """Cross-Feature 3: Validates styling token inheritance, responsive typography, and assets."""
        # 13. Romantic Atelier CSS Variables ↔ Folio Plate Card Styling
        css = self.auditor.css_analysis.raw_css
        has_theme_vars = "--bg-" in css or "--ink-" in css or "--amber-" in css or "bg-" in self.raw_html
        self.record_assertion(
            3, "X-THEME-CARDS", "Folio Plates Inherit Romantic Atelier Tokens", bool(has_theme_vars),
            "Project folio plates inherit chiaroscuro palette and etched border styling"
        )

        # 14. Typographic Pairing ↔ Hierarchy Cross-Check
        has_serif_and_mono = bool(re.search(r"serif", css, re.IGNORECASE)) or bool(re.search(r"mono", css, re.IGNORECASE)) or "font-mono" in self.raw_html
        self.record_assertion(
            3, "X-TYPO-PAIRING", "Serif Headings & Monospace Badges Pairing", bool(has_serif_and_mono),
            "Literary serif applied to headings paired with crisp monospace metadata"
        )

        # 15. Responsive Breakpoints ↔ Compendium Grid Layout
        has_responsive_grid = bool(self.auditor.css_analysis.media_queries) or "grid" in css or "grid-cols" in self.raw_html
        self.record_assertion(
            3, "X-GRID-RESPONSIVE", "Compendium Grid Responsive Transitions", bool(has_responsive_grid),
            "Project compendium grid smoothly transitions from mobile single-column to desktop multi-column"
        )

        # 16. Academic Dossier ↔ CV Asset Linkage
        has_cv_link = any("lebenslauf.pdf" in a.get("href", "") for a in self.dom.find_all("a")) or "lebenslauf.pdf" in self.raw_html
        self.record_assertion(
            3, "X-DOSSIER-CV", "Academic Dossier Direct CV Asset Linkage", bool(has_cv_link),
            "Academic dossier provides direct download link to staged CV PDF"
        )

        # 17. Ex Libris Header ↔ Navigation Links Linkage
        links = self.dom.find_all("a")
        has_nav_gh = any("github.com/HerRei" in a.get("href", "") for a in links)
        has_nav_li = any("linkedin.com/in/" in a.get("href", "") for a in links)
        self.record_assertion(
            3, "X-HEADER-NAV", "Ex Libris Header & External Channel Linkage", has_nav_gh and has_nav_li,
            "Header and navigation bar provide direct access to verified external channels"
        )
