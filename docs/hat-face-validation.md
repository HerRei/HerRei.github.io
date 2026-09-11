# Face model study validation — 2026-09-10

Updated the portfolio's LocalSR entry, the showcase FAQ, and model notes; added
`localsr/models/` for HAT-S/HAT-L interpolation results and exact checkpoint IDs.
The page identifies this as later-release work and keeps release metadata,
installer links, checksums, and the ongoing v0.0.12 work unchanged.

Validation:

- Static site validator: four HTML pages, local links/assets, anchors, image
  provenance, and release destinations passed.
- Portfolio content suite: 30 tests passed.
- Portfolio interactive engine: 34 assertions passed.
- LocalSR comparison JavaScript tests passed.
- Python model metadata was compared with both published HTML checkpoint records.
- Browser preview was attempted through the browser skill, but the runtime
  reported no available browsers. Visual desktop/mobile inspection is pending;
  no rendered or accessibility-conformance claim is made.

Metrics are summaries of the existing HAT-S report and the operator's Task 4
HAT-L report, not new evaluations. The published example image still uses SPAN;
no face samples or model weights were added.

## Video preview follow-up

The preview page now documents SeedVR2's SDR-only selection, output-resolution
control, real processing phases, and memory limits. The reported native MPS
failure was reproduced and followed by a successful ten-frame, three-clip
256×454 SDR export from a 4K HLG input in 266.5 seconds. This is a functional
small-output check, with no claim of 4K/8K feasibility or restoration quality.
The desktop app also completed a separate five-frame SeedVR2 export and a
two-frame HAT-S job with visibly aligned render squares and a first-frame ETA.

The updated five-page static validation and all six comparison JavaScript tests
passed. Existing release links and installer metadata remain unchanged. The
browser-runtime limitation above still applies to website visual inspection.

## Frame and playback follow-up — 2026-09-11

The preview notes now describe the current source frame beneath HAT's translucent
grid, actual overlapping SeedVR2 VAE regions, and whole-frame diffusion activity.
They also explain reduced-resolution detail loss and the completed-video player
fix for returning to previously selected media.

The native app completed a five-frame 256×454 SDR SeedVR2 export and displayed its
real encode/decode regions. A bounded full-input-resolution HAT-S run showed the
source, tile geometry and measured first-frame ETA; it was cancelled before full
inference completed. The player opened both exported files and successfully
returned to the first comparison after viewing the next one. The small SeedVR2
output remains visibly soft; this is not a full-resolution restoration claim.

Application checks: 557 Python passed / 2 skipped, 68 frontend passed, 48 Rust
passed, Svelte checks clean, native macOS debug build passed. The five-page site
validator and six comparison JavaScript tests passed. The website changes are
text updates within the existing page layout; no new browser rendering claim is made.

## AMD and platform follow-up — 2026-09-12

The preview notes now describe AMD ROCm support, real GPU/RAM diagnostics,
upstream block offloading and small-tile memory controls. They distinguish
short successful 4K/720p SeedVR2 checks from long-video and restoration-quality
acceptance, and explicitly retain the visible VAE seam limitation.

The installed Linux application passed playback and returning to a completed
video while another job ran. Packaged CPU and AMD workers passed real image,
video, trim/audio, tile/ETA, cancellation and retry checks. Native Windows tests
and the frozen CPU worker also passed on a disposable hosted VM. These findings
are preview evidence; Windows GPU and signed-installer acceptance remain open.

Static validation passed for all five pages, along with six comparison tests,
30 portfolio content tests and 34 interactive-engine assertions. This is a prose
update in the existing layout. No browser was opened on the user's current Mac,
and no new rendered-layout claim is made. Release metadata, downloads and the
v0.0.12 release process were left unchanged.

The preview explicitly marks the final Windows rerun of the later timing fixes
as outstanding. Earlier successful native/worker checks do not certify that
follow-up, Windows GPU drivers or signed installation.
