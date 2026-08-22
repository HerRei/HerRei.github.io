#!/usr/bin/env python3
"""
Adversarial tests for the three specimens and the index line.

These execute nothing — they read the shipped script and assert the
properties that would be expensive to discover in a browser: that the
nocturne's frequencies really are the notes it names, that the telemetry
figure cannot drift into nonsense, that the departure panel is honest
about being a redrawing.

    python3 -m unittest tests.test_adversarial_interactive_engines -v
"""

from __future__ import annotations

import math
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOC = (PROJECT_ROOT / "index.html").read_text(encoding="utf-8")
JS = re.search(r"<script>(.*?)</script>", DOC, re.S).group(1)

# Equal temperament, A4 = 440 Hz
SEMITONES = {"C": -9, "C♯": -8, "D": -7, "E♭": -6, "E": -5, "F": -4,
             "F♯": -3, "G": -2, "A♭": -1, "A": 0, "B♭": 1, "B": 2}


def expected_hz(note: str) -> float:
    match = re.fullmatch(r"([A-G][♯♭]?)(\d)", note)
    pitch, octave = match.group(1), int(match.group(2))
    return 440.0 * 2 ** (SEMITONES[pitch] / 12 + (octave - 4))


class TestNocturne(unittest.TestCase):
    """The score must be the music it claims to be."""

    def setUp(self):
        self.score = re.findall(
            r'\{ f: ([\d.]+), n: "([^"]+)",\s*d: ([\d.]+), c: "([^"]+)" \}', JS
        )

    def test_score_is_present_and_finite(self):
        self.assertEqual(len(self.score), 20, "the nocturne is twenty notes long")

    def test_every_frequency_matches_its_note_name(self):
        for freq, note, _dur, _chord in self.score:
            with self.subTest(note=note):
                self.assertAlmostEqual(
                    float(freq), expected_hz(note), delta=0.6,
                    msg=f"{note} is written as {freq} Hz, but {note} is {expected_hz(note):.2f} Hz",
                )

    def test_every_note_lies_within_a_piano(self):
        for freq, note, _d, _c in self.score:
            with self.subTest(note=note):
                self.assertTrue(27.5 <= float(freq) <= 4186.0,
                                f"{note} at {freq} Hz is off the keyboard")

    def test_durations_are_sane(self):
        for freq, note, dur, _c in self.score:
            with self.subTest(note=note):
                self.assertTrue(0.2 <= float(dur) <= 3.0, f"{note} lasts {dur}s")

    def test_it_opens_and_closes_on_the_tonic(self):
        self.assertEqual(self.score[0][1], "D3", "the nocturne opens on D")
        self.assertEqual(self.score[-1][1], "D3", "and resolves back to D")
        self.assertIn("resolution", self.score[-1][3])

    def test_harmonics_are_integer_multiples(self):
        partials = re.findall(r'\{ type: "(\w+)",\s+mult: (\d), level: ([\d.]+) \}', JS)
        self.assertEqual(len(partials), 3, "fundamental plus two partials")
        multipliers = [int(m) for _t, m, _l in partials]
        self.assertEqual(multipliers, [1, 2, 3], "partials are the first three harmonics")
        levels = [float(l) for _t, _m, l in partials]
        self.assertEqual(levels, sorted(levels, reverse=True),
                         "higher harmonics are quieter, as on a string")

    def test_the_envelope_cannot_click_or_clip(self):
        self.assertIn("gain.gain.setValueAtTime(0.0001, now)", JS, "it starts from silence")
        self.assertIn("exponentialRampToValueAtTime(0.0001", JS, "and decays to silence")
        peak = float(re.search(r"linearRampToValueAtTime\((0\.\d+), now \+ 0\.014\)", JS).group(1))
        self.assertLess(peak * 3, 1.0, "three partials at peak stay below full scale")

    def test_audio_is_never_started_without_a_click(self):
        calls = [m.start() for m in re.finditer(r"\bnocturne\.play\(", JS)]
        self.assertEqual(len(calls), 1, "the nocturne is started from exactly one place")
        handler = JS.index('playBtn.addEventListener("click"')
        self.assertGreater(calls[0], handler,
                           "the only call to play() sits inside the click handler")


class TestTelemetrySpecimen(unittest.TestCase):
    """Fig. 1 must stay inside plausible hardware limits, forever."""

    def test_loss_is_bounded_below(self):
        self.assertIn("Math.max(0.94, loss", JS, "loss cannot decay towards zero")

    def test_step_counter_wraps_instead_of_overflowing(self):
        self.assertIn("step = step < total ? step + 1 : 1;", JS)

    def test_reported_values_stay_within_the_card(self):
        vram_base, vram_jitter = 21800, 90
        self.assertIn(f"({vram_base} + Math.floor(Math.random() * {vram_jitter}))", JS)
        self.assertLess(vram_base + vram_jitter, 24564, "VRAM used never exceeds VRAM present")

        temp = re.search(r"\((\d+) \+ Math\.floor\(Math\.random\(\) \* (\d+)\)\) \+ \" °C\"", JS)
        self.assertLess(int(temp.group(1)) + int(temp.group(2)), 95, "temperature stays sane")

        power = re.search(r"\((\d+) \+ Math\.floor\(Math\.random\(\) \* (\d+)\)\) \+ \" W\"", JS)
        self.assertLess(int(power.group(1)) + int(power.group(2)), 600, "power draw stays sane")

    def test_eta_cannot_go_negative(self):
        self.assertIn("Math.max(0, Math.floor((total - step) * 0.8))", JS)

    def test_the_figure_admits_what_it_is(self):
        self.assertIn("invented numbers", DOC,
                      "the caption must not imply a live GPU")


class TestDeparturePanel(unittest.TestCase):
    """Fig. 3 is a redrawing of a real panel, and says so."""

    def test_clock_is_zero_padded(self):
        self.assertIn('pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds())', JS)
        self.assertIn('String(n).padStart(2, "0")', JS)

    def test_rows_are_plausible_swiss_services(self):
        rows = re.findall(r'<span class="panel-line">([^<]+)</span>'
                          r'<span class="panel-dest">([^<]+)</span>', DOC)
        self.assertEqual(len(rows), 3)
        for line, destination in rows:
            with self.subTest(line=line):
                self.assertRegex(line, r"^(S\d+|IC\d+|IR\d+|RE\d*)$")
                self.assertTrue(destination.strip())

    def test_departure_times_are_ordered(self):
        times = [t for t in re.findall(r'<span class="panel-time">(\d\d):(\d\d)</span>', DOC)]
        minutes = [int(h) * 60 + int(m) for h, m in times]
        self.assertEqual(minutes, sorted(minutes), "a departure board is ordered by time")

    def test_the_figure_admits_what_it_is(self):
        self.assertIn("not a photograph of it", DOC)


class TestIndexLine(unittest.TestCase):
    """The filter is the only thing on the page that hides content."""

    def test_categories_are_compared_as_tokens(self):
        self.assertIn('(entry.getAttribute("data-category") || "").split(/\\s+/)', JS)
        self.assertIn('cats.indexOf(cat) !== -1', JS)

    def test_state_is_mirrored_into_aria(self):
        self.assertIn('btn.setAttribute("aria-pressed"', JS)

    def test_filtering_is_reversible(self):
        self.assertIn('entry.classList.toggle("is-hidden", !show)', JS,
                      "hiding uses a class that 'all' removes again")

    def test_the_function_is_exposed_for_scripting(self):
        self.assertIn("window.filterCategory = filterCategory;", JS)


class TestCanvasGeometry(unittest.TestCase):
    """The oscilloscope must not be drawn into a squashed backing store."""

    def test_backing_store_follows_the_element(self):
        self.assertIn("canvas.width = Math.round(cssW * dpr)", JS)
        self.assertIn("canvas.height = Math.round(cssH * dpr)", JS)
        self.assertIn("pen.setTransform(dpr, 0, 0, dpr, 0, 0)", JS)

    def test_the_trace_is_plotted_in_css_pixels(self):
        self.assertIn("var slice = cssW / bins", JS)
        self.assertIn("var y = (data[i] / 128.0) * cssH / 2", JS)

    def test_the_stave_has_five_lines(self):
        self.assertIn("for (var i = -2; i <= 2; i++)", JS)

    def test_it_redraws_when_the_window_changes(self):
        self.assertIn('window.addEventListener("resize"', JS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
