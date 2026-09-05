# Portfolio verification

The current checks exercise the static content, the existing interactive engines,
and the rendered botanical portfolio.

## Fast checks

```sh
python3 tests/run_e2e_tests.py
node tests/test_interactive_engine_stress.js
```

The Python runner checks document nesting, duplicate IDs, local assets, local
fragments, artwork provenance, and the existing 25 music, telemetry, filter, and
canvas assertions. `tests/challenger1_stress_suite.py` is a compatibility entry
point for the current structural checks.

The Node suite executes the actual inline script with a stub DOM and a virtual
clock. It tests filtering and counts, 10,000 randomized filter changes, 10,000
telemetry ticks, pause/resume, audio scheduling, canvas sizing, and reduced motion.

## Browser checks

Install test-only dependencies outside the site:

```sh
npm install --prefix /tmp/herrei-portfolio-qa --no-save playwright @axe-core/playwright
node /tmp/herrei-portfolio-qa/node_modules/playwright/cli.js install chromium
NODE_PATH=/tmp/herrei-portfolio-qa/node_modules node tests/portfolio_browser.cjs
```

The test opens the local HTML by default. Set `PORTFOLIO_BASE_URL` to test a hosted
copy. Set `PORTFOLIO_QA_DIR` to choose where screenshots, the accessibility reports,
the print PDF, and the JSON summary are written; the default is a directory inside
the operating system's temporary folder.

It checks 320, 390, 768, 1440, and 1920 pixel widths, text/container overflow,
all loaded images, automated WCAG A/AA rules at desktop and mobile widths,
every filter and result count, keyboard navigation, the display disclosure,
telemetry stepping, real Web Audio start/stop, nonblank canvas pixels,
200% text resizing, print after filtering, and no-JavaScript reading.

Automated accessibility checks are not a conformance certification. Inspect the
screenshots as well; these tests cannot decide whether artwork and typography
are well composed. Audio scheduling tests do not evaluate musical quality.

## Replaced catalogue expectations

The earlier `tier1_*` through `tier4_*` modules and their parser helpers describe
the previous printed-catalogue design. They assert intentionally removed choices
such as paper grain, Google-hosted Bodoni/Garamond, Roman wall labels, and one
inline stylesheet. They are retained as historical reference but are not called
by the current runner. The new browser suite replaces their layout and visitor
journey coverage, and the relevant engine assertions remain active.

## LocalSR

```sh
python3 localsr/tools/validate_site.py
node --test localsr/tests/comparison.test.cjs
```

The portfolio refresh preserves the existing LocalSR pages and release assets.
