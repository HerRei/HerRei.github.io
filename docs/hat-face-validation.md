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
