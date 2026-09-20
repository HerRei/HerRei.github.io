# herrei.github.io

Hermes Reisner's site is now at [hermesreisner.com](https://hermesreisner.com/).
The root of this repository only redirects there.

What still lives here is the **LocalSR showcase** at
[herrei.github.io/localsr/](https://herrei.github.io/localsr/): the pages, downloads,
guides, and the update feed that installed LocalSR apps poll at launch. Nothing under
`localsr/` may move or change its URL. The showcase has its own
[maintenance notes](localsr/README.md).

## Structure

- `index.html`: the redirect to hermesreisner.com. The old page's bookmarks
  (`#catalogue`, `#notice`, `#correspondence`, `#methods`) land on the matching pages.
- `localsr/`: the LocalSR showcase, maintained independently.
- `docs/`: design and validation notes for the showcase, and the HAT face-restoration
  validation record.

There is no framework or build step. GitHub Pages serves the root of `main`.

The previous portfolio, with its design study and tests, was retired on 20 September 2026
and is in the history up to commit `81aba53`.
