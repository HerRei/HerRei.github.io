# LocalSR social-preview artwork

The link-preview graphic is [`localsr/assets/og.png`](../localsr/assets/og.png), 1200 × 630 pixels.
It is rendered from [`localsr-og-card.html`](localsr-og-card.html) in the site's own typeface, with the
butterfly example from the home page (a real LocalSR result, see `localsr/assets/examples/provenance.json`).

To render it again, serve the repository root and screenshot the card at exactly 1200 × 630:

```sh
python3 -m http.server 8766 --bind 127.0.0.1
# then, with Playwright or any headless browser:
#   viewport 1200 × 630, open http://127.0.0.1:8766/docs/localsr-og-card.html, screenshot to localsr/assets/og.png
```

Keep `og:image:width` and `og:image:height` in `localsr/index.html` in step with the image.
The earlier paper-style card (1738 × 905, made with an image generator) is in the history up to commit `b7e2636`.
