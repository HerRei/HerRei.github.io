# Portfolio refresh validation

5 September 2026. See the [design study](portfolio-design-study.md) for the
research, alternative evaluation, and project-content audit.

## Scope

The homepage has a contemporary botanical layout, credited woodland artwork,
self-hosted typography, real project imagery, revised descriptions for all ten
projects, and clearer routes to source, demonstrations, the CV, and contact.
The LocalSR showcase and its existing release work are preserved. The starting
point included upstream commit `21f41d6`; no repository visibility was changed.

## Results

| Check | Result |
| --- | --- |
| Current Python content and engine assertions | 30 passed |
| Executed inline JavaScript and virtual-clock stress checks | 34 passed, including 10,000 filter changes and 10,000 telemetry ticks |
| LocalSR structural, asset, provenance, and release validator | Passed |
| LocalSR comparison interaction tests | 6 passed |
| Browser sizes | 320 x 568, 390 x 844, 768 x 1024, 1440 x 1000, 1920 x 1080 |
| Layout and imagery at all five sizes | No horizontal or checked text overflow; all images loaded |
| Automated accessibility at 390 and 1440 pixels | Zero violations in the tested WCAG A/AA rules |
| Filters | All six categories, counts, pressed states, membership, and reset passed |
| Keyboard | Skip link, Space activation of a filter, and native disclosure passed |
| Browser specimens | Reduced-motion telemetry, manual stepping, Web Audio start/stop, and nonblank canvas pixels passed |
| Enlarged text | 200% text size at both 1440 and 390 pixels passed without overflow |
| No JavaScript | All ten projects and the CV remain available; inactive controls are hidden |
| Print | All ten projects are included even after filtering to hardware |
| Runtime | No page errors in the browser run |
| Patch hygiene | `git diff --check` passed |

Screenshots were inspected for the desktop and mobile opening, the complete page,
project imagery, and overall reading order. The browser runner also saves a print
PDF and detailed machine-readable accessibility reports. Local artifacts are in
`/tmp/herrei-portfolio-qa-results/` for this run; they are not published as site
content. The in-app Browser runtime reported no available browser, so validation
used a local headless Chromium installation through Playwright.

The earlier design-specific static tiers are not a current acceptance criterion:
they assert the deliberately replaced antique palette, Google Fonts, and wall
labels. Current structural checks and real browser journeys replace that coverage.
The substantive music, telemetry, filtering, and canvas checks remain active.

## Links and content

All 19 non-LinkedIn external destinations returned HTTP 200, including the public
GitHub repositories, seven project demonstrations, the artwork attribution, and
the official Basel-Stadt inventory map. The map does not accept the initial HEAD
request but works with GET and redirects to MapBS. The checker now handles this
distinction. Local page, asset, and fragment links were checked against the files.

LinkedIn returns its automated-access rejection (HTTP 999 on GET). The existing
profile URL agrees with the owner's public GitHub profile, but its destination
content was not independently verified. No login or account change was attempted.

LocalSR's application repository is absent from the public repository list. The
homepage therefore links to the public showcase and alpha release notes, and does
not promise publicly accessible application source or publish private code.

## Loading and contrast

The desktop woodland WebP is 318,038 bytes; the mobile version is 128,984 bytes.
The HTML is approximately 35 KB, the stylesheet approximately 18 KB, and the three
reused local font files total approximately 71 KB. Other project images are
lazy-loaded. Width and height are declared to reserve space. These are file sizes,
not field performance measurements; no LCP or INP percentile claim is made.

Measured solid-color contrast ratios include:

| Foreground / background | Ratio |
| --- | ---: |
| Main text / page | 13.80:1 |
| Secondary text / page | 6.23:1 |
| Green links / page | 9.06:1 |
| Green text / sage | 7.82:1 |
| Secondary text / sage | 5.38:1 |
| Music label / lilac | 6.69:1 |

The artwork's text band uses 91% opaque dark green, giving the white text a
predictable background even over light image pixels. The photograph and painting
themselves have no color wash or blur. Controls include visible focus and
text-labelled state, and reduced motion prevents the waveform animation from
being restarted into a continuous loop.

## Limits and publication

This is local Chromium verification, not a full accessibility certification,
physical-device test, musical listening test, or multi-browser certification.
External repository activity can change after the review date. The design study's
option scores are explicit judgments, not analytics or results from user testing.

Publication uses the existing GitHub Pages source, `main` at the repository root.
The release is the commit that adds this record. Confirm its Pages build and the
public HTML after pushing. A normal revert of that commit provides rollback.
