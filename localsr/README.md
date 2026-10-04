# LocalSR showcase

Published at **https://herrei.github.io/localsr/**. The site is static HTML on
[Tufte CSS](https://edwardtufte.github.io/tufte-css/) (vendored in `vendor/tufte/`, MIT, with the
self-hosted ET Book faces) plus one site stylesheet and a small progressive-enhancement script.
There is no build step. Its download links and content remain usable without JavaScript.

Read the [redesign record](../docs/localsr-redesign-2026-09.md) for the current visual direction
and the [original design study](../docs/localsr-design-study.md) for the product audit, references
and evidence policy, which still apply. The design that preceded the September 2026 redesign is kept
unchanged under `previous/` (its pages carry `noindex` and point back to the current site); it is a
frozen snapshot and the release tools do not update it.

## Files

- `index.html`, `styles.css`, `showcase.js`: the home page and its real image comparison.
- `vendor/tufte/`: Tufte CSS and the ET Book fonts, unmodified, with their licenses.
- `guide/`: the user guide the app opens from Help → LocalSR User Guide.
- `models/`: every catalog model in plain words, the license table and the face-model evidence.
- `release-notes/`: public, readable release notes for the current beta.
- `download/`, `support/`, `privacy/`: download page, support, and the privacy page that must
  describe every count the site, the app and the download hosts make.
- `about-the-image/`: source photography, model credit, and image preparation.
- `release.json`: authoritative application release metadata.
- `SHA256SUMS`: installer checksums generated from that metadata.
- `assets/image-provenance.json`: exact model/source/output provenance, and the provenance of
  the app screenshot `assets/localsr-desktop.webp` (an unedited capture from the app repository).
- `assets/fonts/`: self-hosted font subsets and SIL Open Font License notices. The LocalSR pages
  no longer use them; the portfolio at the repository root still does, so they stay.
- `previous/`: the archived September 2026 design, kept as it was.
- `tools/`: release synchronizer and reproducible image preparation.

## Updating the app release

Update `release.json` with verified GitHub release asset names, sizes, checksums, platform
requirements, and the version. Installers and source bundles are downloaded from the GitHub
release (`https://github.com/HerRei/local-upscale/releases/download/<tag>/<file>`), which a
home connection could not serve to many people at once. Then run:

```sh
python3 localsr/tools/sync_release.py
python3 localsr/tools/sync_release.py --check
```

The script updates the download rows, version labels, and checksums. Update the displayed release
date and prose in `index.html` and `release-notes/index.html` to match actual release acceptance.
Refresh social-preview text when the version changes: `assets/og.png` is rendered from a small
HTML card with headless Firefox (see the redesign record), not drawn by hand. Do not carry forward claims about a new
backend, signing, or physical testing without release evidence.

## Visit counting

Every page loads `count.js`, which sends
`GET https://macmini-ci.tail34a4e0.ts.net/hit?p=<page path>&r=<external referrer host>` to the
LocalSR stats collector on the Mac mini (the same Caddy host that serves `/releases/`). It skips
Do Not Track, Global Privacy Control, and anything not served from `https://herrei.github.io`.
The server keeps only daily totals; see `privacy/index.html` for the public description, which must
change whenever the counting changes. `tools/validate_site.py` fails if a page lacks the script.

## Reproducing the image

Use LocalSR's Python environment with its verified Quick Start model already installed:

```sh
/path/to/LocalSR/.venv/bin/python localsr/tools/prepare_demo.py --localsr /path/to/LocalSR
```

The optional `--source` argument reuses a local copy of the source photograph; `--device mps`
uses Apple Silicon. Results can differ slightly across numerical backends. The committed
provenance records the device and precision used for the published example. The lossless
comparison assets are actual inference output, not the high-resolution source or CSS filters.

## Validation and publication

Run these checks, then the portfolio's existing checks documented in the root README:

```sh
python3 localsr/tools/validate_site.py
node --check localsr/showcase.js
node --test localsr/tests/comparison.test.cjs
```

The Pages repository publishes
from the root of `main`. Website releases use a `localsr-site-v…` tag to distinguish them from
application releases. There is no separate hosting service or build framework.

## Publishing an app update

Installed LocalSR apps (v0.1.0-beta and later) check
`https://herrei.github.io/localsr/updates/<channel>.json` at launch. The Beta
channel reads `updates/beta.json`; Stable reads `updates/stable.json` and ignores
pre-releases.

1. Build, sign and notarize the new version in the LocalSR repository
   (`build/release-<version>/release_macos.sh`). It also writes the signed
   `.app.tar.gz` update archive, its `.sig`, the source bundle and `release.json`.
2. Upload the update archive, its `.sig` and the engine payload files to the Mac mini under
   `/mnt/hdd/localsr-downloads/public/releases/v<version>/`, and publish the DMG, the source
   bundle and `SHA256SUMS` as assets of the GitHub release `v<version>`.
3. Edit `updates/beta.json`: raise `version`, update `notes` and `pub_date`, and
   in `platforms["darwin-aarch64-mps-native"]` set the new `url`, the contents of
   the `.sig` file as `signature`, and the `localsr` contract (`engine_id`, `size`,
   `unpacked_size`, `sha256` from the release's `release.json` and `SHA256SUMS`).
4. Update `release.json` for the download page, run `python3 tools/sync_release.py`
   and `python3 tools/validate_site.py`, then commit and push.

Apps pick the update up the next time they start. Never publish a feed entry
before the exact files it names are uploaded and downloadable.
