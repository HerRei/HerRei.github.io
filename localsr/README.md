# LocalSR showcase

Published at **https://herrei.github.io/localsr/**. The pages are static HTML with one stylesheet
and two small progressive-enhancement scripts. Download links and content work without JavaScript.

The look follows the desktop app's design language (`desktop/src/styles.css` in the app repository):
neutral dark greys, IBM Plex Sans, 2 px and 4 px corners, and one red (#b3452a) used only on
download buttons. The [design study](../docs/localsr-design-study.md) still
holds the evidence policy; its paper look was replaced in November 2026.

## Files

- `index.html`, `showcase.js`: the home page and its example viewer (real results, a draggable line).
- `styles.css`: the only stylesheet, for every page except the in-browser demo.
- `site.js`: on every page: marks the current section under "On this page", keeps table roles for
  tables that stack on phones, closes the small-screen menu.
- `assets/examples/`: the home page examples, cut from real runs; `provenance.json` lists sources,
  crops, models, the computer each ran on, and checksums that `validate_site.py` checks.
- `compare/`, `models/which/`: measured comparisons; `compare/compare.js` drives their sliders.
- `guide/`: the user guide the app opens from Help → LocalSR User Guide.
- `models/`: every catalog model in plain words, the license table and the face-model evidence.
- `release-notes/`: public, readable release notes for the current beta.
- `download/`, `support/`, `privacy/`: download page, support, and the privacy page that must
  describe every count the site, the app and the download hosts make.
- `about-the-image/`: where each example comes from, how it was prepared and which model made it.
- `release.json`: authoritative application release metadata.
- `SHA256SUMS`: installer checksums generated from that metadata.
- `assets/image-provenance.json`: exact model/source/output provenance.
- `assets/fonts/`: IBM Plex Sans (the app's own unmodified variable file, and the italic converted
  to WOFF2 without other changes), IBM Plex Mono, and their SIL Open Font License notices. DM Sans
  and Newsreader belong to the earlier design and are no longer used.
- `tools/`: release synchronizer and reproducible image preparation.

## Updating the app release

Update `release.json` with verified release asset names, sizes, checksums, platform
requirements, and the version. Public downloads use
`https://github.com/HerRei/local-upscale/releases/download/<tag>/<file>`. The Mac
mini keeps a copy at `https://downloads.hermesr.duckdns.org/releases/<tag>/<file>`
(through the Infomaniak VPS and WireGuard), which the site does not link.
Stage files under `/mnt/hdd/localsr-downloads/staging/`, verify their sizes and
SHA-256 hashes, and install them under `public/releases/<tag>/` before publishing
any website or updater URL. Then run:

```sh
python3 localsr/tools/sync_release.py
python3 localsr/tools/sync_release.py --check
```

The script updates the download rows, version labels, and checksums. Update the displayed release
date and prose in `index.html` and `release-notes/index.html` to match actual release acceptance.
Refresh social-preview text when the version changes. Do not carry forward claims about a new
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
node --test localsr/tests/
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
2. Publish every installer, source bundle, update archive, signature, engine manifest and part, `.sha256`
   file and `SHA256SUMS` as assets of the GitHub release `v<version>`, and copy them to the Mac mini under
   `/mnt/hdd/localsr-downloads/public/releases/v<version>/`. Both the download page and updater must use `https://github.com/HerRei/local-upscale/releases/download/v<version>/`.
3. Edit `updates/beta.json`: raise `version`, update `notes` and `pub_date`, and
   in `platforms["darwin-aarch64-mps-native"]` set the new `url`, the contents of
   the `.sig` file as `signature`, and the `localsr` contract (`engine_id`, `size`,
   `unpacked_size`, `sha256` from the release's `release.json` and `SHA256SUMS`).
4. Update `release.json` for the download page, run `python3 tools/sync_release.py`
   and `python3 tools/validate_site.py`, then commit and push.

Apps pick the update up the next time they start. Never publish a feed entry
before the exact files it names are uploaded and downloadable.
