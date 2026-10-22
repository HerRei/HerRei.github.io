#!/usr/bin/env bash
# Rebuild the browser demo at localsr/demo/ from a LocalSR release tag.
# usage: tools/localsr-demo/build.sh <path to a local-upscale checkout> [tag]
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
site="$(cd "$here/../.." && pwd)/localsr/demo"
app="${1:?path to a local-upscale checkout}"
tag="${2:-v0.2.1-beta}"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git -C "$app" archive "$tag" desktop src/localsr/core/edit_catalog.json | tar -x -C "$work"
cp -R "$here/src/tour" "$work/desktop/src/"
cp "$here/tour.html" "$here/vite.demo.config.ts" "$work/desktop/"
(cd "$work/desktop" && npm ci --no-audit --no-fund && npx vite build --config vite.demo.config.ts)
python3 "$here/finish_page.py" "$work/desktop/dist-demo" "$site"
