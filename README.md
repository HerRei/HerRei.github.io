# herrei.github.io

A catalogue of ten works in software and hardware, set as a printed exhibition
catalogue: warm paper, iron-gall ink, one vermillion pigment, each work given a
wall label — medium, date, where it is kept.

Live at **<https://herrei.github.io/>**.

LocalSR has a dedicated [showcase](https://herrei.github.io/localsr/) with a real image
comparison, alpha downloads, and release notes. Its [design study](docs/localsr-design-study.md)
and [maintenance notes](localsr/README.md) live in this repository.

## What is here

```
index.html   the portfolio — one file, no framework, no build step
assets/      the portrait and the curriculum vitae
localsr/     LocalSR showcase, comparison images, downloads, and alpha notes
docs/        the LocalSR design study and social artwork brief
tests/       four suites; see TESTS.md
```

The portfolio fetches its typefaces from Google Fonts
(Bodoni Moda for display, EB Garamond for text, JetBrains Mono for the
specimens). There is no bundler, no package.json, no CI step: GitHub Pages
serves the static files as they are committed. The LocalSR showcase self-hosts its fonts
and comparison images.

## Working on it

Open `index.html` in a browser. That is the whole loop.

Before pushing:

```sh
python3 tests/run_e2e_tests.py                    # 210 assertions, four tiers
python3 tests/challenger1_stress_suite.py         # adversarial static checks
PYTHONPATH=. python3 -m unittest tests.test_adversarial_interactive_engines
node tests/test_interactive_engine_stress.js      # runs the page's own script
```

## Conventions worth knowing

**The three figures are re-creations, and say so.** Fig. 1 draws invented
telemetry, Fig. 2 plays a hand-written motif rather than the model's output,
Fig. 3 redraws the ST7789 layout rather than photographing it. If a caption
ever stops saying that, the tests fail.

**Dates are the day each repository first appeared publicly**, not the day the
work began. The colophon states this. A work with no public repository is dated
`n.d.` and marked *private collection* rather than linked to a 404.

**The index line's tallies are checked against reality.** Adding a work means
adding its `data-category` and correcting the `<span class="tally">` counts —
four separate suites will refuse the change otherwise.

**Horizontal padding belongs to `.sheet`.** Setting a `padding` shorthand on
`.section` or `.title-page` silently cancels the page gutter and flattens every
section against the viewport edge below 62rem. There is a regression test.
