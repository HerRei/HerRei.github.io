# LocalSR — showcase design study

5 September 2026 · Design direction and implementation brief

## 1. The job of this page

Make a small, independent desktop application understandable and worth trying. A visitor should
recognize image restoration, inspect an actual result, understand that processing stays on their
computer, and find the installer for their operating system. The site belongs at
`https://herrei.github.io/localsr/`, within the existing public portfolio repository.

The primary audience is photographers and people with an image they want to enlarge: an old
JPEG, an illustration, a scan, or a photograph with limited resolution. They need visible evidence
and a straightforward explanation more than a list of model architectures. A second audience of
technical early adopters needs exact platform support, model provenance, and release limitations.

The central message: **Give your images a little more room.** Supporting copy names the actual
operations—upscale, denoise, deblur—and the local desktop workflow. “SR” is explained as
super-resolution rather than assumed knowledge.

## 2. Product audit

The implementation baseline is the LocalSR repository at v0.0.11-alpha, including its README,
known limitations, model catalogue, automation command, and Tauri/Svelte interface source.

| Evidence | Consequence for the site |
| --- | --- |
| Image enlargement at 2×, 3×, and 4×; native-size denoising and deblurring | Lead with enlargement; explain restoration in a short second section. |
| Media is processed locally; weights are downloaded separately; no app analytics | Explain the initial model download and subsequent local processing. Avoid implying the website or every network request is offline. |
| Quick Start uses SPAN NomosUni | Use this exact engine for the published comparison, with a reproducible input and output. |
| Preview, batch queue, model choice, ICC-aware output | Describe a small, useful workflow. Do not imply all source metadata is preserved. |
| Current interface is Tauri/Svelte with an isolated Python worker | Update the older portfolio entry, which still says PySide6. Keep architecture detail out of the sales copy. |
| v0.0.11-alpha has three installers | Offer macOS Apple Silicon, Windows x86-64, and Linux x86-64 downloads. |
| Windows/Linux installers ship CPU inference; macOS ships MPS | Put the actual backend beside each installer. Do not advertise general NVIDIA/AMD support. |
| Alpha is unsigned; ARM package has static inspection but no physical-device acceptance | State this near installation, with a readable release note for the full context. |
| Video and SeedVR2 are Labs / Experimental | Present video as a secondary experimental capability. |
| Some third-party model terms are unresolved | Do not claim blanket commercial licensing for all models. |

The owner explicitly wants the public-facing download flow prepared before repository access is
opened. Buttons therefore use the real versioned GitHub release asset URLs. The site must not
claim that public access, signing, beta acceptance, or future hardware support is already complete.
No repository visibility or application release changes are part of the website deployment.

## 3. Reference study

These are references for communication and structure, not templates to copy.

| Reference | Relevant observation | Application to LocalSR |
| --- | --- | --- |
| [Halide](https://halide.cam/) | Connects photographic results, image comparison, physical camera controls, and privacy to a specific photographic practice. | Use the language of looking closely at a photograph. Make the comparison the main demonstration. |
| [RICOH GR III / IIIx](https://www.ricoh-imaging.co.jp/english/products/gr-3/) | Gives photographs, product character, features, and specifications distinct places in the information structure. | Let the main image breathe; move exact compatibility to the download section. |
| [darktable](https://www.darktable.org/) | Describes its role in a photographer's workflow concretely, then supplies installation and learning routes. | Explain open → choose → compare → save; keep documentation close to download. |
| [Upscayl](https://www.upscayl.org/) | Establishes enlargement with an image comparison and prominent acquisition routes. | A comparison and platform download choice are useful category conventions. LocalSR needs its own voice and evidence. |
| [Existing portfolio](https://herrei.github.io/) | The local source uses exhibition labels, warm paper, ink, and individual descriptions of each work. | Carry forward the care of a printed catalogue, with a more contemporary photographic treatment for this product. |

## 4. Chosen direction: the photographic work print

The page should feel like a carefully typeset insert accompanying a useful photographic
instrument. Its personality comes from composition, captions, material color, and honest detail.

**Composition.** A narrow masthead, a large asymmetric headline, a short introduction, and one
expansive photographic comparison. The rest of the page alternates between quiet text on paper
and a dark technical plate for the workflow. Numbered section labels sit on shared alignment
lines. A large closing download section completes the reading rhythm.

**Typography.** A sturdy, contemporary grotesque for navigation, headings, and the wordmark;
Newsreader italic for the human phrase in the headline; a restrained monospace for filenames,
dimensions, version numbers, and labels. Self-host a small Latin font subset with fallback fonts
and `font-display: swap`. Keep body copy readable at 16–18 px and comfortable line lengths.

**Palette.** Warm off-white paper (`#f3f1e9`), near-black ink (`#242720`), subdued olive secondary
ink (`#5c6357`), pale sage (`#e0e5d7`), and a small vermilion accent (`#b33d26`). The photograph
provides the rich color. Use solid fields and hairline borders. Controls have compact corners.

**Image choice.** An architectural photograph has small, inspectable edges, balcony railings,
repeating structures, concrete texture, and natural color. It suits the geometric layout and gives
the comparison something specific to show. The selected photograph is Tim Ziegelbaum's
[Unité d'Habitation in Marseille](https://unsplash.com/photos/modern-apartment-building-with-colorful-balconies-against-blue-sky-n4bofMDUS_Y),
available under the [Unsplash License](https://unsplash.com/license). Credit the photographer.

**Evidence treatment.** Produce a low-resolution input by resizing the licensed photograph, then
run LocalSR's real Quick Start engine. Show the input and the resulting output at the same visual
size. Disclose the downsampling and exact dimensions. A detail view may use identical crops of
these two files. Do not add blur to the “before,” substitute the original high-resolution image
for the “after,” or promise recovered historical detail. This is one worked example, not a
benchmark or a guarantee.

**Distinctive details.** Small registration marks around the image, a useful comparison divider,
a compact view selector, document-style captions, numbered workflow steps, and a release stamp.
Each has a role. Avoid invented customer counts, awards, testimonials, star fields, glow effects,
generic icon tiles, fake app screenshots, and repeated marketing superlatives.

## 5. Page sequence

1. **Masthead:** LocalSR wordmark; Results, How it works, Download navigation.
2. **Introduction:** “Give your images a little more room.” Plain explanation and Download alpha
   action. A small version marker makes the development stage visible immediately.
3. **The image study:** Large interactive comparison, full-frame/detail controls, real dimensions,
   engine attribution, and a short explanation of the input preparation.
4. **The local workflow:** A dark, calm section with three sequential decisions: open your image,
   choose the treatment, inspect and save. The same result appears as a small work print.
5. **Useful particulars:** Enlargement, native-size restoration, file/color handling, and the
   experimental status of video, in editorial rows rather than identical floating cards.
6. **Download:** Explicit alpha label; three platform-specific installer rows; version, backend,
   format, checksums, release notes, and a short development-status statement.
7. **Questions and colophon:** Local processing, model downloads, what alpha means, model terms;
   author, photography credit, portfolio link, and back to top.

## 6. Interaction and accessibility

The image slider supports a pointer, touch, and the keyboard through a native range input.
Provide an explicit label, a visible focus indication, and before/after actions so using a dragging
gesture is optional. Full-frame and detail controls are buttons with pressed state and retain the
divider position. Captions update with the selected view. Images have descriptive alt text.

At narrow widths, the headline, introduction, and technical rows stack. The image remains usable
without horizontal page scrolling. Navigation fits without a hamburger overlay. Targets are at
least 44 px in the main controls. Honor reduced motion; do not autoplay or move the slider for
the visitor. Content, release notes, and downloads work without JavaScript; enhanced comparison
controls appear only after successful initialization.

## 7. Implementation and publication

Preserve the portfolio's static HTML architecture. Add an isolated `/localsr/` directory with
HTML, CSS, a small progressive-enhancement script, local fonts, optimized image assets, release
metadata, and a readable release-notes page. Do not add a framework or build dependency solely
for this site. Use a single shared release configuration for maintaining the download links.

Keep an image provenance record and a script to reproduce the demonstration from the source
photo and LocalSR CLI. Produce a dedicated landscape social card in the same visual system and
inspect its text before including it in link-preview metadata. It is a graphic, never result evidence.

Validation covers document structure, internal links, asset existence and dimensions, download
manifest consistency, JavaScript syntax, meaningful comparison interactions, and the existing
portfolio checks. Publish the validated changes to the public Pages repository and verify the
deployed HTTP responses and served revision. Create a website-specific prerelease with the
design study and publication notes; do not modify the application's v0.0.11-alpha release.

## 8. Definition of done

A working public URL, real interactive before/after evidence, three explicit alpha download
buttons, accurate development information, a consistent visual identity at small and large
widths, documented assets and provenance, a retained design study, and a website release in
the hosting repository. Future work is updating download access and release metadata as the
application becomes public and its platform acceptance progresses.
