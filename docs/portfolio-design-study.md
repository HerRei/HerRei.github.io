# Portfolio refresh: a contemporary botanical direction

5 September 2026. Design study and implementation brief for [herrei.github.io](https://herrei.github.io/).

## 1. Recommendation

Keep the portfolio's personal, exhibition-like character, but give it the clarity of a contemporary independent studio. Use forest green, a credited woodland painting, a restrained serif display face, and clear sans-serif body text. Let the projects supply most of the visual variety. Present useful descriptions, real images, project status, and direct routes to demonstrations and source.

The proposed direction is **a botanical portfolio**, not an environmental consultancy identity. Trees and art are the owner's requested visual interests. They should not imply that every project concerns sustainability, that the owner painted the artwork, or that the work has an environmental impact that has not been measured.

The recommendation is a design judgment informed by professional guidance and a repository audit. No visitor analytics, interviews, conversion study, or A/B test were available. The comparative scores below make the priorities explicit; they are not measured user outcomes.

## 2. Baseline and audience

The baseline is the public portfolio at commit `21f41d6`, including the recent LocalSR showcase. The site is plain HTML, CSS, and JavaScript published from `main` through GitHub Pages. This is appropriate for a small portfolio: the content is immediately available, publishing is simple, and there is no application service to maintain.

The existing page gives ten projects equal space in a long, narrow catalogue. It has thoughtful captions and working browser specimens, but the antique paper palette, tightly spaced small labels, Roman numerals, and formal vocabulary compete with a straightforward understanding of the work. The large opening title describes a category; the person's name is less prominent. The contact copy is unnecessarily dismissive. Several technically specific project claims no longer match their current READMEs.

Three likely visitor tasks guide the redesign:

1. A collaborator or recruiter needs the person's identity, area of work, relevant examples, and a contact or CV link.
2. A developer needs a concise description, the actual stack, an honest distinction between a browser demonstration and the underlying application, and the repository.
3. A curious visitor needs an inviting visual introduction and a few understandable projects before choosing where to explore.

These are plausible task models, not validated audience segments. The page should serve them without requiring the visitor to select a persona or read introductory instructions.

## 3. Professional references and their limits

| Primary reference | Relevant guidance | Application and limit |
| --- | --- | --- |
| [IBM Carbon: typography style strategies](https://carbondesignsystem.com/elements/typography/style-strategies/) | Expressive typography supports exploration and editorial reading; productive typography supports task completion. The approaches can coexist. | A distinctive serif name and section headings, with compact sans-serif navigation and readable project descriptions. This borrows the distinction, not IBM's brand identity or complete component system. |
| [IBM Design Language: 2x Grid](https://www.ibm.com/design/language/2x-grid/) | A consistent grid, gutters, base spacing, and common image ratios create relationships between otherwise different content. | Align headings, images, captions, and links to a shared grid. Use two project columns on wide screens and one on small screens. Variation comes from content and emphasis, not arbitrary offsets. |
| [GOV.UK Design System: type scale](https://design-system.service.gov.uk/styles/type-scale/) | A limited scale of sizes and line heights supports readable, consistent pages; relative units support resizing. | Use a small rem-based scale and generous body line height. Avoid tiny metadata and viewport-scaled text. Government-service branding is not appropriate for this personal portfolio. |
| [GOV.UK Design System: images](https://design-system.service.gov.uk/styles/images/) | Images must have a purpose and accessible alternatives; essential information should remain available as text. | Real project imagery helps visitors understand the work. The painting expresses the requested artistic identity and is visibly credited. All project meaning and links remain in HTML. This portfolio has a stronger expressive purpose than a transactional service. |
| [IBM Design Language: photography tips](https://www.ibm.com/design/language/photography/tips-and-techniques/) | Clear, purposeful imagery and honest subject portrayal are preferable to vague visual metaphors or heavy effects. | Keep the hardware photograph and LocalSR output inspectable. Do not invent a nature-inventory map or substitute a fabricated screenshot. The woodland painting is artwork, not evidence of a project result. |
| [W3C: contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | Ordinary text requires 4.5:1 contrast and large text 3:1 for the AA criterion, subject to the criterion's exceptions. | Measure the actual palette. Avoid small text directly over variable image pixels. Provide a predictable solid contrast treatment where text overlays the artwork. |
| [W3C: reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) | Ordinary content should work at a width equivalent to 320 CSS pixels without two-dimensional scrolling. | Check the longest name, email, metadata, filters, and specimens at narrow widths. Use explicit wrapping and single-column flow. |
| [W3C: target size minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | The AA criterion specifies 24 by 24 CSS pixels, with spacing and other exceptions. | Aim for 44-pixel primary controls as a design margin. Use native buttons for filters, visible focus, and useful accessible names. Do not imply the 44-pixel choice is the AA minimum. |
| [W3C: focus not obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) | Author-created overlays must not entirely obscure keyboard focus. | Keep navigation simple, account for header height when following anchors, and check keyboard traversal. |
| [web.dev: Web Vitals](https://web.dev/articles/vitals) | User experience includes loading, responsiveness, and layout stability. Good field thresholds are LCP at most 2.5 seconds, INP at most 200 milliseconds, and CLS at most 0.1 at the 75th percentile. | Reserve image dimensions, prioritize the hero image, lazy-load later images, reuse local fonts, and keep the site static. Local checks are diagnostics, not proof of real-user percentile performance. |

## 4. Options evaluated

Scores are subjective, from 1 (poor fit) to 5 (strong fit). Weights reflect the request for a modest artistic update that still functions as a professional portfolio.

| Criterion | Weight | Green recolor of the catalogue | Botanical editorial portfolio | Immersive animated forest |
| --- | ---: | ---: | ---: | ---: |
| Finding and understanding projects | 30% | 3 | 5 | 2 |
| Artistic and natural character | 25% | 3 | 5 | 5 |
| Accessibility and mobile resilience | 20% | 4 | 4 | 2 |
| Maintenance and loading cost | 15% | 5 | 4 | 1 |
| Continuity with the existing site | 10% | 5 | 4 | 2 |
| Weighted score out of 5 | 100% | **3.70** | **4.55** | **2.60** |

A recolor is inexpensive and retains every structural choice, but it leaves the central content problem unresolved: too much cataloguing before a visitor can compare projects. It also risks turning the entire page into shades of green without introducing meaningful imagery.

An immersive forest could be memorable, but a scene with camera movement, particles, or scrolling interactions would dominate the work and introduce performance, accessibility, and maintenance costs. There is no demonstrated portfolio task that requires it.

The botanical editorial direction has a clear cost: an image increases transfer size and makes contrast more difficult. Responsive compressed assets, a short hero, a predictable text background, and real project visuals address those issues. It can retain the existing browser specimens without asking them to carry the identity of the whole page.

The conclusion is reasonably stable if maintenance receives more weight: even moving ten percentage points from artistic character to maintenance leaves the recommended direction ahead of the recolor. If the owner instead required an almost image-free page or a strict sub-100 KB total budget, the recolor would become the appropriate choice.

## 5. Visual specification

### Composition

Use a compact masthead with direct Work, About, and Contact anchors. Make Hermès Reisner the main heading in the first viewport. The woodland artwork spans the introduction, without a decorative preview card. Keep the opening short enough that subsequent content is suggested on common desktop and mobile screens.

Follow with a brief, plain introduction and the work catalogue. LocalSR leads because it has a substantial new showcase; the nature-inventory project follows because it connects the botanical identity to an actual technical interest. The remaining work includes systems, music, embedded hardware, a team game, algorithms, and small tools. A shared two-column structure lets people compare projects with less scrolling than the old one-project-per-band layout. On mobile, document order becomes a single readable column.

An About section carries the existing portrait, verified biographical information, practical skill groups, and CV. A short contact section uses welcoming, direct wording. Artwork attribution belongs in the footer and beside the image, not buried in a dependency file.

### Palette and typography

Use a cool near-white ground, charcoal ink, and deep forest green for emphasis. A pale lilac secondary field and a small rust accent provide contrast; project images add their own colors. Avoid making every surface a different green, or carrying over the old beige-and-brown cast.

Reuse the existing self-hosted DM Sans, Newsreader italic, and IBM Plex Mono assets where appropriate. DM Sans handles ordinary reading and controls. Newsreader supplies occasional expressive italic headings, with a serif fallback. Mono is restricted to technical labels and the existing specimens. Fonts have explicit fallback stacks and `font-display: swap`.

Keep letter spacing at zero. Use rem sizes with discrete responsive adjustments, not typography tied to viewport width. Body text should remain comfortably readable, with descriptions generally limited to two or three short sentences and roughly 60 characters per line. Numeric metadata should not compete with titles.

### Artwork

Use Gustav Klimt's *Beech Grove I* (circa 1902), from the Galerie Neue Meister in Dresden. The [Wikimedia Commons file record](https://commons.wikimedia.org/wiki/File:Gustav_Klimt_-_Beech_Grove_I_-_Google_Art_Project.jpg) identifies the reproduction and public-domain status and links to the museum's collection record. Its repeated vertical trunks give the page a recognizably wooded, artistic opening. Credit Klimt and link to the source; do not imply ownership of the painting.

The web asset may be resized and compressed, and the hero shows a crop appropriate to its wide format. Keep a route to the complete composition. Do not recolor, blur, animate, or generate extra trees. Record derivatives and source information in `assets/portfolio/provenance.json`. The painting's historical date is an intentional artistic reference; the contemporary quality comes from layout and communication, not from pretending the work is new.

## 6. Project-content audit

The public GitHub repository list and current README files were checked on 5 September 2026. Repository descriptions alone are insufficient: several disagree with their own documentation. The homepage should use the narrower supported statement.

| Project | Decision |
| --- | --- |
| LocalSR | Lead with local desktop image enlargement and link to the existing `/localsr/` showcase. Call it an alpha. Do not invent a public source link: the application repository is absent from the public repository listing. Do not duplicate a volatile version number on the homepage. |
| Nature Inventory Delta | Describe local comparison of Basel-Stadt inventory versions, maps, charts, and optional language-model queries. Name FastAPI, Streamlit, and SQLite. Explicitly note that a prepared database is required and is not included. |
| train-tui | Describe the dependency-free C training dashboard, named framework profiles, and AMD/NVIDIA telemetry sources. Remove unsupported millisecond-startup or interrupted-SSH guarantees. Keep the browser sample explicitly simulated. |
| GPT-2 piano | Describe MIDI-conditioned continuation, REMI tokenization, and Apple Silicon training. Treat the 12k dataset as MIDI files, not 12,000 distinct recorded performances. Distinguish the hand-written homepage audio specimen from generated model output. |
| ESP32 departure board | Use a real photograph from the project repository, plus the existing clearly labelled browser reconstruction. Mention OpenData updates, display filtering, and watchdog recovery. |
| PhantomHunt | Identify it as a University of Basel team project. Attribute the owner's work to networking, lobby and game-state handling, scoring, and related backend work. The current README says Java 25. |
| TSP / ant colony | Explain the adjustable Java visualizer and browser demonstration. Do not call the New York dataset a benchmark unless a reproducible benchmark is supplied. |
| Google Sheets automation | Replace unsupported automatic-import and idempotency claims with the actual guided record-entry workflow using Flask, Python, OAuth, and the Sheets API. |
| Telegram YouTube player | Replace the outdated Linux/MPV-only description. The README now describes supported browsers, monitor selection, persistent queues, and Windows, macOS, and Linux. |
| PhantomHunt prototype | Retain as an early browser experiment, clearly distinct from the final team game. Avoid invented comparative findings about which pathfinding method won. |

Sources: [public profile](https://github.com/HerRei), [LocalSR showcase](https://herrei.github.io/localsr/), and the README linked from each named project on the page. Supporting repositories such as the Homebrew tap are distribution infrastructure rather than separate featured projects. Forks are not represented as original work. No private repository is published or made public as part of this refresh.

## 7. Interaction and implementation

Preserve plain static hosting and existing paths, including CV, project sub-sites, and the LocalSR release pages. Preserve old section fragments where practical so saved links continue to work. Keep project content in HTML: it must be available without JavaScript and without a live GitHub API request.

Filters are an enhancement over the complete list. A selected state must have a visual indicator beyond color, expose `aria-pressed`, and announce the visible result count. Derive counts from the entries to prevent stale hand-maintained tallies. If JavaScript is unavailable, show the full catalogue and suppress controls that cannot work.

Retain the telemetry, piano, and display specimens with honest captions, explicit playback controls, and existing reduced-motion behavior. Do not autoplay sound. Their visual appearance can become quieter without changing their core domain logic. On print, include all projects even if the interactive filter currently hides some.

Use local image assets with width and height, responsive sources where helpful, and deliberate loading priority. Do not add an analytics service, contact-form backend, framework, or content system to solve this small static-site task. A short maintenance note should identify where projects, counts, artwork provenance, and tests live.

## 8. Acceptance and release

Before publication, check the page at 320, 390, 768, 1440, and wide desktop widths. Inspect screenshots for overlap, readable text, loaded images, and sensible framing. Check keyboard focus, all filter states, reset to all projects, project and contact links, JavaScript-disabled reading, reduced motion, and print output. Check that the preserved interactive engines still pass their relevant existing tests.

The previous static suites include assertions about the deliberately replaced antique palette, typefaces, and layout. Update those design-specific expectations where appropriate; do not claim an old design snapshot is proof of the new experience. Browser checks should exercise user-visible behavior rather than reproduce CSS declarations as assertions.

Record what was actually tested, any limitations, asset weight, and the final commit in a validation note. Run checks again only when a correction changes behavior. Commit the completed work, push to the existing `main` branch as requested, and confirm the GitHub Pages build and public response. Preserve any intervening upstream commits before pushing. A standard revert of the refresh commit is the rollback path.

After release, a useful qualitative follow-up would be to ask a few unfamiliar visitors to find one relevant project and the CV. That would test the scanability assumption. There is no basis to claim the redesign improves hiring or engagement until that evidence exists.
