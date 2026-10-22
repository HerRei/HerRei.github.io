"""Install a demo build into localsr/demo/ and add what the site needs.

usage: finish_page.py <vite dist-demo dir> <site localsr/demo dir>

The built tour.html becomes index.html with the site's favicon, canonical
address, visit counter and a heading for the page outline. The media folder in
the destination is kept: it holds the recorded run and is not rebuilt.
"""

import shutil
import sys
from pathlib import Path

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
html = html.replace("  </head>", head_extra + "  </head>")
html = html.replace('<div id="app">', heading.lstrip() + '    <div id="app">')
html = html.replace(
    "<p>Loading LocalSR…</p>",
    "<p>Loading LocalSR…</p><noscript>The demo runs the LocalSR interface and needs JavaScript.</noscript>",
)
(destination / "index.html").write_text(html, encoding="utf-8")
print("installed", destination)
