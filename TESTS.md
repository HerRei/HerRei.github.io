# Tests

Four suites, no third-party dependencies — Python 3.10+ and Node for the last
one. They read (and, in one case, execute) the shipped `index.html`; there is
nothing to build first.

| Suite | Run it with | What it covers |
|---|---|---|
| Four-tier E2E | `python3 tests/run_e2e_tests.py` | Features, boundaries, feature combinations, whole visitor journeys |
| Adversarial stress | `python3 tests/challenger1_stress_suite.py` | Strict markup parse, hostile viewports, filter fuzzing, asset signatures, scripts assuming nothing exists |
| Engine assertions | `PYTHONPATH=. python3 -m unittest tests.test_adversarial_interactive_engines` | The music theory, the telemetry bounds, the panel's plausibility |
| Executed script | `node tests/test_interactive_engine_stress.js` | Runs the page's own script against a stub DOM and a virtual clock |

Useful flags on the E2E runner: `--tier {1,2,3,4}`, `--verbose` (prints every
assertion), `--json` (machine-readable).

## The four tiers

**Tier 1 — features (F1–F13).** Paper and pigments; typography; the ten wall
labels; the index line; provenance; the three specimens; honest captions;
accessibility; the responsive sheet; the print sheet; assets; restrained
motion; architecture.

**Tier 2 — boundaries.** The sparsest filter, the work with no public
repository, entries without figures, date formats, page and asset weight, long
strings, the narrowest screen.

**Tier 3 — combinations.** Filtering against printing, filtering against the
specimens, provenance against the index, declared tokens against the ones
actually used, reduced motion against every moving part, headings against
sections.

**Tier 4 — journeys.** An engineer looking for source; someone hiring, reading
and printing; a reader on a phone with no audio; someone on a keyboard with a
screen reader.

## The shared machinery

`tests/dom_parser.py` is a small standalone HTML parser and selector engine.
`tests/static_analyzer.py` parses the inline CSS and JS — note that it reads
custom properties only from top-level `:root` blocks, keeping `@media print`
overrides separate in `conditional_properties`, so the printed palette is never
reported as the screen's. `tests/test_base.py` records assertions so the runner
can tabulate them.

## What the suites are for

They exist to catch the things that are cheap to get wrong and expensive to
notice: a tally that no longer matches the works it filters, a link to a
repository that has gone private, a caption that starts claiming a photograph
is of hardware it never depicted, a padding shorthand that cancels the page
gutter. Every assertion should be one you would actually want to be told about.
Assertions that merely read the stylesheet back to itself are not worth having.
