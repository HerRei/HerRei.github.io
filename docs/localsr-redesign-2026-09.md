# LocalSR site — September 2026 redesign

20 September 2026 · Design record

## Why

The first site (5 September 2026, [design study](localsr-design-study.md)) carried the portfolio's
printed-catalogue vocabulary: warm paper, a serif italic in every headline, a vermilion accent and
numbered section labels. That vocabulary has since become the default look of generated marketing
pages. A first rebuild on the system font with a large bold headline and a blue button read, in the
owner's words, "still very AI coded": it was the default look of generated developer landing pages.

The owner asked for a framework that is genuinely uncommon and a page that does not look generated,
while keeping everything the site does and hosting it unchanged on GitHub Pages.

## Direction: a book page, on Tufte CSS

The site is now built on [Tufte CSS](https://edwardtufte.github.io/tufte-css/) (MIT, by Dave
Liepmann), vendored unmodified at `localsr/vendor/tufte/` with the five ET Book faces it needs
(MIT, Dmitry Krasny, Bonnie Scranton and Edward Tufte). It is a small, opinionated stylesheet for
articles in the manner of Tufte's books: a 55% text column, a margin for numbered sidenotes,
full-width figures, small-caps lead-ins, old-style numerals, and its own dark scheme.

It fits LocalSR because the site's whole policy is evidence: a real comparison, a provenance
record, model tables with measured results, checksums. That is a monograph's apparatus, not a
landing page's. Nothing generated uses this framework, and the page cannot be mistaken for a
template: there is no hero, no card grid, no pill button, no gradient.

`localsr/styles.css` is the site's own layer on top: a running head, the comparison figure and its
text-only controls, download rows, tables set with rules above and below, code blocks, and the
narrow-screen behaviour of notes (they become indented notes under their line instead of Tufte's
hidden toggles, so nothing is concealed from readers or screen readers).

## Tokens

- **Type.** ET Book throughout, self-hosted (five `.woff` files, about 220 KB). Body text is
  21 px on 30 px lines, notes and captions 16.5 px, nothing below 15 px. Headings are Tufte's:
  a 48 px roman title, italic section heads.
- **Colour.** Tufte's page `#fffff8` and ink `#111` (18.9:1); dates and asides `#6b6b6b`
  (5.3:1); rules `#ccc`. Dark appearance follows the system with Tufte's `#151515` and `#ddd`,
  asides `#a3a3a3` (7.2:1). The one colour is the red square of the app icon, `#b33d26`, used
  as the period after the name, exactly as the app's title bar does.
- **Layout.** Tufte's: body 87.5% of the viewport up to 1400 px, text at 55%, notes in the
  margin, figures at 90% when full width. Under 760 px everything is one column.
- **Signature.** Actual pixels. In "A closer look" the input crop is drawn without smoothing, so
  one input pixel appears as the 4 × 4 block it becomes; the caption says so with two tiny
  drawn squares. The one piece of decoration on the page, and it is the product's promise.
- **Motion.** None beyond the divider following the pointer.

## What stayed

Every page, section id, download link and claim; `release.json`, `SHA256SUMS`, `updates/*.json`,
`count.js` on every page, `showcase.js` untouched (its six interaction tests pass unchanged), the
`sync_release.py` markers and row markup, the no-JavaScript fallbacks, skip link, focus rings,
reduced motion and forced-colours rules. The secondary pages' bodies moved into the new frame
verbatim; their old side navigation became a contents line under the title. The home page shows
the unedited app screenshot from the app repository (v0.1.1-beta, M1 Pro, NASA Apollo 17
photograph, "NASA does not endorse LocalSR"), with provenance and checksum in
`assets/image-provenance.json`, verified by `tools/validate_site.py`.

The design that preceded this one is archived unchanged at `/localsr/previous/` (noindex, counter
pointed at the live script, one-line notice) and linked from the footer.

## Social card

`assets/og.png` (1200 × 630) is rendered from an HTML card with headless Firefox, set in ET Book
like the site. It is a graphic, not result evidence.

## Checks

`python3 localsr/tools/validate_site.py`, `node --check localsr/showcase.js`,
`node --test localsr/tests/comparison.test.cjs`, the root portfolio runner, and headless Firefox
renderings at 390 and 1440 px in both appearances.
