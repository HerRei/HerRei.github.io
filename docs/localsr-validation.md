# LocalSR showcase — publication checks

5 September 2026

## Passed

- HTML validation of all three pages with `html-validate`: no errors or warnings.
- Local page links, fragment targets, fonts, image assets, image alternatives/dimensions, button
  types, and document language verified by `localsr/tools/validate_site.py`.
- Download metadata, filenames, SHA-256 sums, and visible release version match `release.json`.
  Release values were checked against the GitHub API for the existing v0.0.11-alpha assets.
- Comparison source and output hashes match the retained provenance record. The published
  output is from the LocalSR automation pipeline, using its verified SPAN NomosUni checkpoint.
- Six interaction tests exercise the shipped comparison script: initialization, before/after
  endpoints, accessible state, paired image swapping, rapid view changes, and load failures.
- JavaScript syntax and Git whitespace checks pass.
- All 210 assertions in the existing portfolio suite pass. The former prohibition on any link
  from the private-source LocalSR entry now checks its existing local showcase destination.
- Existing portfolio stress checks pass: 41 static assertions, 25 Python tests, and 34 executed
  JavaScript assertions.
- Main text color pairs pass WCAG AA contrast for normal text. The lowest tested ratio is
  5.14:1 (vermilion on paper); secondary body text is 5.50:1.
- Local HTTP serving returns 200. All three fonts have valid WOFF2 headers and retain their
  license notices. The social card was inspected for text accuracy.

## Scope of verification

The in-app browser runtime reported no available browser. No browser screenshot, rendered
layout inspection, real-device touch check, or native keyboard interaction claim is made. The
site has responsive CSS, native range controls, focus states, reduced-motion behavior, and
JavaScript-free download/navigation fallbacks; interaction tests use controlled image loading.

The website's download destinations intentionally point to the application's existing release
assets. Anonymous access depends on the application's later public distribution decision.
This website publication does not change repository visibility, signatures, installers, or
application development status.

After pushing the validated source, verify the GitHub Pages build commit and the public HTTP
responses for the home page, both supporting pages, styles, script, imagery, fonts, and checksums.
