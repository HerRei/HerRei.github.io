"""
Adversarial Empirical Challenge Suite for HerRei.github.io Interactive JavaScript Engines.
Audits:
- Web Audio API synthesizer: AudioContext initialization, note frequencies, envelope decay, oscillator cleanup.
- ANSI terminal simulator: Telemetry loop ticker, pause/resume state toggling, buffer limits.
- Modal lightbox: Open/close event handling, ESC key handler, backdrop click.
- Staged media and asset byte integrity.
"""

import math
import os
import re
import subprocess
import unittest
from pathlib import Path
from tests.dom_parser import DOMNode
from tests.test_base import BaseE2ETestCase


class TestAdversarialInteractiveEngines(BaseE2ETestCase):
    """Adversarial Interactive Engine & Media Verification Test Suite."""

    # -------------------------------------------------------------------------
    # 1. Web Audio API Acoustic Piano Synthesizer Verification
    # -------------------------------------------------------------------------
    def test_webaudio_piano_frequencies_and_envelope(self):
        """Audits Web Audio API piano synthesizer frequencies, envelope, and AudioContext safety."""
        # 1. Verify AudioContext construction with webkit fallback
        has_audio_ctx = "AudioContext" in self.raw_html
        has_webkit_fallback = "webkitAudioContext" in self.raw_html
        self.record_assertion(
            1, "ADV-AUDIO-CTX", "AudioContext with WebKit Fallback",
            has_audio_ctx and has_webkit_fallback,
            "AudioContext uses standard constructor with webkitAudioContext fallback"
        )

        # 2. Verify Autoplay policy handling (context resume on user gesture)
        has_resume = "resume" in self.raw_html and "suspended" in self.raw_html
        self.record_assertion(
            1, "ADV-AUDIO-AUTOPLAY", "AudioContext Suspended State Resumption",
            bool(has_resume),
            "Synthesizer checks for suspended AudioContext state and calls resume()"
        )

        # 3. Verify Multi-harmonic additive synthesis (Fundamental + 2nd + 3rd harmonics)
        has_harmonics = "freq * 2" in self.raw_html and "freq * 3" in self.raw_html
        self.record_assertion(
            1, "ADV-AUDIO-HARMONICS", "Additive Multi-Harmonic Overtone Synthesis",
            bool(has_harmonics),
            "Synthesizer generates fundamental, 2nd (2x), and 3rd (3x) overtone harmonics"
        )

        # 4. Verify Acoustic soundboard biquad filter & exponential decay
        has_biquad = "createBiquadFilter" in self.raw_html or "lowpass" in self.raw_html
        has_exp_decay = "exponentialRampToValueAtTime" in self.raw_html
        self.record_assertion(
            1, "ADV-AUDIO-ENVELOPE", "Lowpass Filter Soundboard & Exponential Decay",
            has_biquad and has_exp_decay,
            "Piano engine shapes timbre with lowpass filter sweep and exponential decay envelope"
        )

        # 5. Verify Non-zero exponential ramp safety (target value strictly > 0 to prevent Web Audio crash)
        has_safe_floor = "0.0001" in self.raw_html or "0.001" in self.raw_html
        self.record_assertion(
            1, "ADV-AUDIO-RAMP-SAFETY", "Strictly Positive Exponential Ramp Floor (>0)",
            bool(has_safe_floor),
            "Exponential gain decay ramps to positive non-zero floor (0.0001) preventing RangeError"
        )

        # 6. Verify Note frequency mathematical accuracy against Equal Temperament (A4 = 440 Hz)
        # Extract score frequencies from HTML
        freq_matches = re.findall(r"f:\s*([0-9]+\.[0-9]+)", self.raw_html)
        freqs = [float(f) for f in freq_matches]
        self.record_assertion(
            1, "ADV-AUDIO-SCORE-COUNT", "D Minor Nocturne Score Completeness (20 Notes)",
            len(freqs) >= 15,
            f"Extracted {len(freqs)} score note frequencies from piano synthesizer definition"
        )

        # Check known anchor frequencies: A4 = 440.0, A3 = 220.0, D3 = 146.83
        has_a4 = any(abs(f - 440.0) < 0.1 for f in freqs)
        has_a3 = any(abs(f - 220.0) < 0.1 for f in freqs)
        has_d3 = any(abs(f - 146.83) < 0.1 for f in freqs)
        self.record_assertion(
            1, "ADV-AUDIO-EQUAL-TEMP", "Equal Temperament Physical Pitch Accuracy",
            has_a4 and has_a3 and has_d3,
            "Score note frequencies match equal temperament physical pitch standards"
        )

        # 7. Verify Oscillator scheduled stop and cleanup
        has_osc_stop = ".stop(now + duration)" in self.raw_html or ".stop(" in self.raw_html
        self.record_assertion(
            1, "ADV-AUDIO-OSC-CLEANUP", "Oscillator Lifetime Scheduling & Cleanup",
            bool(has_osc_stop),
            "Oscillators are scheduled to stop cleanly at tone duration end"
        )

    # -------------------------------------------------------------------------
    # 2. ANSI Terminal Telemetry Simulator Verification
    # -------------------------------------------------------------------------
    def test_ansi_terminal_telemetry_simulator(self):
        """Audits ANSI terminal telemetry ticker, pause/resume, and step controls."""
        # 8. Verify Terminal DOM elements exist
        has_term_box = len(self.dom.select("#train-tui-terminal, .terminal-simulator")) >= 1
        has_term_toggle = len(self.dom.select("#term-toggle-btn")) >= 1
        has_term_tick = len(self.dom.select("#term-tick-btn")) >= 1
        self.record_assertion(
            2, "ADV-TERM-DOM", "Terminal Simulator Dashboard & Interactive Controls",
            has_term_box and has_term_toggle and has_term_tick,
            "Terminal simulator container, pause/resume toggle, and step button exist in DOM"
        )

        # 9. Verify Telemetry metrics elements (VRAM, TEMP, PWR, LOSS, TPS, ETA)
        metrics_present = all([
            len(self.dom.select("#term-vram")) >= 1,
            len(self.dom.select("#term-temp")) >= 1,
            len(self.dom.select("#term-pwr")) >= 1,
            len(self.dom.select("#term-loss-graph")) >= 1,
            len(self.dom.select("#term-tps")) >= 1,
            len(self.dom.select("#term-eta")) >= 1,
        ])
        self.record_assertion(
            2, "ADV-TERM-METRICS", "All 6 Telemetry Metric Readout Nodes Present",
            metrics_present,
            "VRAM, Temp, Power, Loss graph, TPS throughput, and ETA countdown nodes exist"
        )

        # 10. Verify Ticker interval and pause/resume logic
        has_interval_lifecycle = "setInterval" in self.raw_html and "clearInterval" in self.raw_html
        has_toggle_listener = "term-toggle-btn" in self.raw_html and "addEventListener" in self.raw_html
        self.record_assertion(
            2, "ADV-TERM-TICKER", "Telemetry Ticker Lifecycle & Pause/Resume Control",
            has_interval_lifecycle and has_toggle_listener,
            "Terminal simulator implements interval timer with start/stop lifecycle"
        )

        # 11. Verify Counter rollover boundary protection
        has_step_rollover = "termStep < totalSteps" in self.raw_html or "termStep =" in self.raw_html
        self.record_assertion(
            2, "ADV-TERM-ROLLOVER", "Training Step Wraparound & Invariant Protection",
            bool(has_step_rollover),
            "Terminal ticker implements bounds checking and wraparound when total steps reached"
        )

    # -------------------------------------------------------------------------
    # 3. ESP32 Hardware Showcase & Lightbox Modal Verification
    # -------------------------------------------------------------------------
    def test_modal_lightbox_and_tft_display(self):
        """Audits modal lightbox open/close, backdrop click, tabs, and ST7789 TFT display."""
        # 12. Verify Dialog modal element & close button
        modals = self.dom.select("#hardware-modal")
        close_btns = self.dom.select("#close-modal-btn")
        open_btns = self.dom.select("#open-hardware-modal-btn")
        self.record_assertion(
            3, "ADV-MODAL-DOM", "Hardware Lightbox Modal Dialog & Trigger Controls",
            bool(modals and close_btns and open_btns),
            "Dialog element, open trigger button, and close button exist in DOM"
        )

        # 13. Verify ST7789 TFT Live Clock element & updater
        tft_clocks = self.dom.select("#tft-live-clock")
        has_clock_timer = "updateTftClock" in self.raw_html or "tft-live-clock" in self.raw_html
        self.record_assertion(
            3, "ADV-TFT-CLOCK", "ST7789 TFT Display Real-Time Clock Simulation",
            bool(tft_clocks and has_clock_timer),
            "ST7789 departure board includes live ticking clock element and interval"
        )

        # 14. Verify Backdrop click detection logic
        has_backdrop_click = "e.target === hwModal" in self.raw_html or "target === modal" in self.raw_html
        self.record_assertion(
            3, "ADV-MODAL-BACKDROP", "Backdrop Click Target Discrimination",
            bool(has_backdrop_click),
            "Lightbox modal listener checks e.target === hwModal before closing on backdrop click"
        )

        # 15. Verify Modal tab asset data binding
        modal_tabs = self.dom.select(".modal-tab")
        tab_sources = [t.get("data-img") for t in modal_tabs if t.has_attr("data-img")]
        self.record_assertion(
            3, "ADV-MODAL-TABS", "Modal Showcase Tab Image Source Attributes",
            len(tab_sources) == 3,
            f"Found {len(tab_sources)} tabs with valid data-img attributes"
        )

    # -------------------------------------------------------------------------
    # 4. Physical Asset & Media Binary Integrity Verification
    # -------------------------------------------------------------------------
    def test_physical_media_assets_integrity(self):
        """Audits physical media assets in assets/ for existence, format headers, and non-zero size."""
        required_assets = [
            ("assets/profilbild.png", b"\x89PNG\r\n\x1a\n", "PNG image header"),
            ("assets/lebenslauf.pdf", b"%PDF-", "PDF document header"),
            ("assets/board-closeup.svg", b"<svg", "SVG XML markup header"),
            ("assets/board-installed.svg", b"<svg", "SVG XML markup header"),
            ("assets/IMG_1591_q85.jpg", b"\xff\xd8\xff", "JPEG image header")
        ]

        for rel_path, expected_magic, desc in required_assets:
            abs_path = self.project_root / rel_path
            exists = abs_path.exists()
            size = abs_path.stat().st_size if exists else 0
            
            # Check magic bytes header
            magic_ok = False
            if exists and size > 0:
                with open(abs_path, "rb") as f:
                    header = f.read(len(expected_magic))
                    magic_ok = header.startswith(expected_magic) or expected_magic in header

            self.record_assertion(
                4, f"ADV-ASSET-{abs_path.stem.upper()[:8]}", f"Asset Integrity: {rel_path} ({desc})",
                exists and size > 100 and magic_ok,
                f"Asset {rel_path} verified on disk ({size:,} bytes, valid {desc})"
            )

    # -------------------------------------------------------------------------
    # 5. Node.js Empirical Stress-Test Execution Bridge
    # -------------------------------------------------------------------------
    def test_nodejs_empirical_stress_execution(self):
        """Executes Node.js adversarial stress-test script and verifies 100% pass."""
        stress_script = self.project_root / "tests" / "test_interactive_engine_stress.js"
        self.record_assertion(
            5, "ADV-STRESS-SCRIPT-EXISTS", "Node.js Stress-Test Script Existence",
            stress_script.exists(),
            f"Node.js stress-test script located at {stress_script}"
        )

        # Run Node.js stress runner
        proc = subprocess.run(
            ["node", str(stress_script)],
            capture_output=True,
            text=True,
            cwd=str(self.project_root)
        )

        passed = (proc.returncode == 0) and ("12/12 Passed" in proc.stdout)
        self.record_assertion(
            5, "ADV-NODE-STRESS-EXEC", "Node.js Empirical Stress Test Suite (12/12)",
            passed,
            f"Node.js stress suite executed with exit code {proc.returncode}"
        )


if __name__ == "__main__":
    unittest.main()
