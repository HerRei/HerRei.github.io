# herrei.github.io

[Hermès Reisner's portfolio](https://herrei.github.io/): software, systems, and
experiments, with a botanical visual direction and ten curated projects.

The [design study](docs/portfolio-design-study.md) documents the source research,
content audit, alternatives, and decisions. The [validation record](docs/portfolio-validation.md)
records the release checks.

## Structure

- `index.html`: project content, navigation, and the small interactive specimens.
- `assets/portfolio/`: stylesheet, compressed artwork, project images, and Lucide icons.
- `assets/portfolio/provenance.json`: image sources, rights, and transformations.
- `assets/`: the existing portrait and CV.
- `localsr/`: the dedicated LocalSR showcase, maintained independently.
- `tests/`: current content, engine, and browser verification; see [TESTS.md](TESTS.md).

There is no framework or build step. GitHub Pages serves the root of `main`.
Open `index.html` locally to preview it. The portfolio reuses the existing
self-hosted DM Sans, Newsreader, and IBM Plex Mono files in `localsr/assets/fonts/`.
Images and fonts require no third-party runtime requests.

## Updating projects

Edit the entries in `index.html`. Project descriptions should match their current
READMEs, state team contributions and development status, and link to public
destinations. LocalSR intentionally links to its showcase and release notes;
its application repository is not currently listed publicly.

Keep category names aligned with the filter buttons. The script calculates their
counts from `data-category`; update the HTML fallback tallies too. The complete
catalogue is readable without JavaScript. The Work, About, Contact, and Methods
section IDs preserve the old bookmark destinations.

The telemetry uses invented values, the piano sample is hand-written, and the
expandable departure specimen uses sample services. Their captions must continue
to distinguish these specimens from real project output. The hardware photograph
and game screenshot are actual project media.

For images, add source and license information to the provenance file. Keep
dimensions explicit and prefer compressed local assets. The woodland painting is
Gustav Klimt's *Beech Grove I*, credited and linked on the page.

## Before publishing

```sh
python3 tests/run_e2e_tests.py
node tests/test_interactive_engine_stress.js
```

Run the browser checks described in [TESTS.md](TESTS.md) for visual or interaction
changes. Commit and push to `main`; confirm the GitHub Pages build completes.
The LocalSR showcase has its own [maintenance notes](localsr/README.md) and checks.
