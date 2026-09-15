# LocalSR showcase

Published at **https://herrei.github.io/localsr/**. The page is static HTML/CSS and a small
progressive-enhancement script. Its download links and content remain usable without JavaScript.

Read the [design study](../docs/localsr-design-study.md) for the product audit, references,
visual direction, page structure, and evidence policy.

## Files

- `index.html`, `styles.css`, `showcase.js`: the showcase and its real image comparison.
- `models/`: HAT-S/HAT-L face-model evidence, manual import, and later-release availability.
- `release-notes/`: public, readable development and installation notes.
- `about-the-image/`: source photography, model credit, and image preparation.
- `release.json`: authoritative application release metadata.
- `SHA256SUMS`: installer checksums generated from that metadata.
- `assets/image-provenance.json`: exact model/source/output provenance.
- `assets/fonts/`: self-hosted font subsets and SIL Open Font License notices.
- `tools/`: release synchronizer and reproducible image preparation.

## Updating the app release

Update `release.json` with verified GitHub release asset names, sizes, checksums, platform
requirements, and the version. Then run:

```sh
python3 localsr/tools/sync_release.py
python3 localsr/tools/sync_release.py --check
```

The script updates the download rows, version labels, and checksums. Update the displayed release
date and prose in `index.html` and `release-notes/index.html` to match actual release acceptance.
Refresh social-preview text when the version changes. Do not carry forward claims about a new
backend, signing, or physical testing without release evidence.

The owner requested real download buttons in advance of public repository access. These links
point to the existing application's versioned release assets. Anonymous downloads will require
the application repository to become public, or the manifest to point to a public distribution
repository. Publishing this site does not change application repository access.

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
2. Upload those files to the Mac mini under
   `/mnt/hdd/localsr-downloads/public/releases/v<version>/`.
3. Edit `updates/beta.json`: raise `version`, update `notes` and `pub_date`, and
   in `platforms["darwin-aarch64-mps-native"]` set the new `url`, the contents of
   the `.sig` file as `signature`, and the `localsr` contract (`engine_id`, `size`,
   `unpacked_size`, `sha256` from the release's `release.json` and `SHA256SUMS`).
4. Update `release.json` for the download page, run `python3 tools/sync_release.py`
   and `python3 tools/validate_site.py`, then commit and push.

Apps pick the update up the next time they start. Never publish a feed entry
before the exact files it names are uploaded and downloadable.
