"""Install a demo build into localsr/demo/ and add what the site needs.

usage: finish_page.py <vite dist-demo dir> <site localsr/demo dir>

The built tour.html becomes index.html with the site's stylesheet, header,
favicon, canonical address, visit counter and a heading for the page outline.
The media folder in the destination is kept: it holds the recorded run and is
not rebuilt.
"""

import re
import shutil
import sys
from pathlib import Path

SITE_HEADER = """<header class="site-header">
  <div class="wrap header-row">
    <a class="logo" href="../" aria-label="LocalSR home"><svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="#ece9df" stroke-width="2.6" d="M3.5 9.5v-6h6M14.5 3.5h6v6M20.5 14.5v6h-6M9.5 20.5h-6v-6"/><rect x="9.25" y="9.25" width="5.5" height="5.5" rx="1" fill="#e0603f"/></svg><span>LocalSR</span></a>
    <nav class="nav" aria-label="Main"><a href="../guide/">Guide</a><a href="../demo/" aria-current="page">Demo</a><a href="../models/">Models</a><a href="../phone/">Mobile app</a><a href="../compatibility/">Compatibility</a><a href="../help/">Help</a><a href="../compare/">vs Upscayl</a></nav>
    <div class="header-end">
      <a class="nav-quiet" href="https://github.com/HerRei/local-upscale">GitHub</a>
      <a class="btn btn-small" href="../download/">Download</a>
      <details class="menu"><summary>Menu</summary><nav aria-label="Main, small screens"><a href="../download/">Download</a><a href="../guide/">Guide</a><a href="../demo/" aria-current="page">Demo</a><a href="../models/">Models</a><a href="../phone/">Mobile app</a><a href="../compatibility/">Compatibility</a><a href="../help/">Help</a><a href="../compare/">vs Upscayl</a><a href="../release-notes/">Release notes</a><a href="https://github.com/HerRei/local-upscale">GitHub</a></nav></details>
    </div>
  </div>
</header>"""

dist, destination = Path(sys.argv[1]), Path(sys.argv[2])
destination.mkdir(parents=True, exist_ok=True)
shutil.rmtree(destination / "assets", ignore_errors=True)
shutil.copytree(dist / "assets", destination / "assets")

html = (dist / "tour.html").read_text(encoding="utf-8")
head_extra = (
    '    <link rel="canonical" href="https://herrei.github.io/localsr/demo/" />\n'
    '    <link rel="icon" type="image/png" href="../assets/favicon.png" />\n'
    '    <script src="../count.js" defer></script>\n'
)
heading = (
    '    <h1 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">'
    "Try LocalSR in your browser</h1>\n"
)
assert html.count("</head>") == 1 and html.count('<div id="app">') == 1
assert html.count("<body>") == 1 and html.count("</body>") == 1
html = re.sub(
    r'(<link rel="stylesheet"[^>]*href="\./assets/tour-[^"]+\.css"[^>]*>)',
    r'<link rel="stylesheet" href="../styles.css" />\n    \1',
    html,
    count=1,
)
assert "../styles.css" in html, "Expected Vite tour CSS link to place site styles before it"
html = html.replace("  </head>", head_extra + "  </head>")
html = html.replace("<body>", "<body>" + SITE_HEADER)
html = html.replace('<div id="app">', heading.lstrip() + '    <div id="app">')
html = html.replace(
    "<p>Loading LocalSR…</p>",
    "<p>Loading LocalSR…</p><noscript>The demo runs the LocalSR interface and needs JavaScript.</noscript>",
)
html = html.replace("</body>", '  <script src="../site.js" defer></script></body>')
(destination / "index.html").write_text(html, encoding="utf-8")
print("installed", destination)
