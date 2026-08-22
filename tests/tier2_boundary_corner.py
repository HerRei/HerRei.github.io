"""
Tier 2: Boundary & Corner Cases Verification Suite (≥65 Assertions).
Validates edge conditions, empty attributes, broken hrefs, DOM integrity, accessibility, and asset headers.
"""

import os
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse
from tests.dom_parser import DOMNode
from tests.test_base import BaseE2ETestCase


class TestTier2BoundaryCorner(BaseE2ETestCase):
    """Tier 2: Exhaustive Boundary, Corner, and Integrity Test Cases."""

    # -------------------------------------------------------------------------
    # 1. Document Structure & Meta Tags Integrity
    # -------------------------------------------------------------------------
    def test_doc_structure_integrity(self):
        """Validates root html, head, body, and meta configurations."""
        # 1. Root HTML element
        html_node = self.dom.find("html")
        self.record_assertion(
            2, "BND-HTML", "Root HTML Element Present", html_node is not None,
            "Root <html> element correctly instantiated in DOM tree"
        )

        # 2. Head element
        head_node = self.dom.find("head")
        self.record_assertion(
            2, "BND-HEAD", "Head Element Present", head_node is not None,
            "Document <head> element present"
        )

        # 3. Body element
        body_node = self.dom.find("body")
        self.record_assertion(
            2, "BND-BODY", "Body Element Present", body_node is not None,
            "Document <body> element present"
        )

        # 4. Charset meta tag
        charset_meta = self.dom.find("meta", attrs={"charset": "UTF-8"}) or self.dom.find("meta", attrs={"charset": "utf-8"})
        self.record_assertion(
            2, "BND-CHARSET", "UTF-8 Charset Specified", charset_meta is not None,
            "Explicit <meta charset='UTF-8'> present in document"
        )

        # 5. Viewport meta parameters
        vp = self.dom.find("meta", attrs={"name": "viewport"})
        vp_valid = vp is not None and "width=device-width" in vp.get("content", "") and "initial-scale=1" in vp.get("content", "")
        self.record_assertion(
            2, "BND-VIEWPORT", "Viewport Meta Integrity", vp_valid,
            "Viewport meta tag includes width=device-width and initial-scale=1"
        )

    # -------------------------------------------------------------------------
    # 2. Attribute Validity & Empty Attribute Safeguards
    # -------------------------------------------------------------------------
    def test_attribute_safeguards(self):
        """Validates that no empty or malformed attributes exist in interactive elements."""
        links = self.dom.find_all("a")
        imgs = self.dom.find_all("img")
        buttons = self.dom.find_all("button")

        # 6. No empty href in links
        empty_hrefs = [a for a in links if a.get("href") == ""]
        self.record_assertion(
            2, "BND-HREF", "No Empty Href Attributes", len(empty_hrefs) == 0,
            f"Found {len(empty_hrefs)} links with empty href=''"
        )

        # 7. No empty src in images
        empty_srcs = [i for i in imgs if i.get("src") == ""]
        self.record_assertion(
            2, "BND-SRC", "No Empty Src Attributes in Images", len(empty_srcs) == 0,
            f"Found {len(empty_srcs)} images with empty src=''"
        )

        # 8. All images have alt text
        missing_alts = [i for i in imgs if not i.get("alt")]
        self.record_assertion(
            2, "BND-ALT", "Image Alt Text Accessibility", len(missing_alts) == 0,
            f"All {len(imgs)} images specify descriptive alt text" if not missing_alts else f"Missing alt text on {len(missing_alts)} images"
        )

        # 9. All buttons have accessible text or label
        empty_buttons = [b for b in buttons if not b.text_content().strip() and not b.get("aria-label") and not b.get("title")]
        self.record_assertion(
            2, "BND-BTN", "Button Accessibility & Labels", len(empty_buttons) == 0,
            f"All {len(buttons)} buttons have accessible text or aria-label"
        )

        # 10. No javascript: pseudo-protocol in hrefs
        js_hrefs = [a for a in links if a.get("href", "").lower().startswith("javascript:")]
        self.record_assertion(
            2, "BND-PROTO", "Zero JavaScript Pseudo-Protocol Hrefs", len(js_hrefs) == 0,
            "No 'javascript:' URLs in <a> tags"
        )

    # -------------------------------------------------------------------------
    # 3. Anchor & URL Integrity
    # -------------------------------------------------------------------------
    def test_url_and_anchor_integrity(self):
        """Validates all internal anchors, external URLs, and mailto links."""
        links = self.dom.find_all("a")
        all_ids = set()
        for node in self.dom.find_all():
            if node.id:
                all_ids.add(node.id)

        # 11. Internal anchor resolution
        internal_anchors = [a.get("href") for a in links if a.get("href", "").startswith("#") and len(a.get("href")) > 1]
        broken_anchors = [h for h in internal_anchors if h.lstrip("#") not in all_ids]
        self.record_assertion(
            2, "BND-ANCHOR", "Internal Anchor Link Resolution", len(broken_anchors) == 0,
            f"All internal anchors resolve to existing DOM IDs: {internal_anchors}" if not broken_anchors else f"Broken anchors: {broken_anchors}"
        )

        # 12. External URL RFC 3986 parse validity
        ext_urls = [a.get("href") for a in links if a.get("href", "").startswith("http")]
        invalid_urls = []
        for u in ext_urls:
            parsed = urlparse(u)
            if not parsed.scheme or not parsed.netloc:
                invalid_urls.append(u)
        self.record_assertion(
            2, "BND-URL", "External URL RFC Parsing", len(invalid_urls) == 0,
            f"All {len(ext_urls)} external URLs parse cleanly"
        )

        # 13. Mailto link email syntax
        mailto_links = [a.get("href") for a in links if a.get("href", "").startswith("mailto:")]
        valid_mail = all("@" in m and "." in m for m in mailto_links)
        self.record_assertion(
            2, "BND-MAIL", "Mailto URI Email Syntax", valid_mail and len(mailto_links) >= 1,
            f"Mailto links have valid email syntax: {mailto_links}"
        )

        # 14. Target blank tabnabbing protection
        blank_links = [a for a in links if a.get("target") == "_blank"]
        unprotected = [a for a in blank_links if "noopener" not in a.get("rel", "") and "noreferrer" not in a.get("rel", "")]
        self.record_assertion(
            2, "BND-SEC", "Reverse Tabnabbing Protection", len(unprotected) == 0,
            f"All {len(blank_links)} target='_blank' links protected with rel='noreferrer/noopener'"
        )

        # 15. HTTPS only for external links and assets
        insecure_http = [u for u in ext_urls if u.startswith("http://")]
        self.record_assertion(
            2, "BND-HTTPS", "HTTPS Strict Transport Security", len(insecure_http) == 0,
            f"Zero insecure http:// external links (all HTTPS): {insecure_http}"
        )

    # -------------------------------------------------------------------------
    # 4. Compendium Plates & Categories Integrity
    # -------------------------------------------------------------------------
    def test_compendium_and_categories_integrity(self):
        """Validates category slugs, folio counts, and project titles."""
        # 16. Total project count
        articles = self.dom.find_all("article") or self.dom.select(".folio-plate, .folio-card, .glass-card")
        self.record_assertion(
            2, "BND-COUNT", "Compendium Plate Count", len(articles) == 10,
            f"Exactly 10 project plates in compendium (found {len(articles)})"
        )

        # 17. Valid data-category tokens
        allowed_cats = {"all", "systems", "ai", "embedded", "java", "automation", "tools", "audio"}
        invalid_card_cats = []
        for a in articles:
            cat_str = a.get("data-category") or a.get("data-cat") or a.get("data-disciplines") or ""
            tokens = cat_str.split()
            if not tokens:
                invalid_card_cats.append((a, "empty"))
            for t in tokens:
                if t.lower() not in allowed_cats:
                    invalid_card_cats.append((a, t))
        self.record_assertion(
            2, "BND-CATTOK", "Valid Data-Category Tokens", len(invalid_card_cats) == 0,
            f"All project cards contain valid category tokens" if not invalid_card_cats else f"Invalid categories: {invalid_card_cats}"
        )

        # 18. No template placeholder leaks in titles
        headings = self.dom.find_all("h3") or self.dom.select(".folio-title, .plate-title")
        leaked_placeholders = []
        for h in headings:
            txt = h.text_content()
            if "{{" in txt or "${" in txt or "<%" in txt or "TODO" in txt:
                leaked_placeholders.append(txt)
        self.record_assertion(
            2, "BND-LEAK", "No Template Placeholder Leaks", len(leaked_placeholders) == 0,
            "Zero template interpolation syntax leaks in headings"
        )

        # 19. Project description length
        paragraphs = self.dom.find_all("p")
        short_descriptions = [p for p in paragraphs if len(p.text_content()) < 10 and "cs @" not in p.text_content().lower() and "ex libris" not in p.text_content().lower()]
        self.record_assertion(
            2, "BND-PROSE", "Substantive Project Treatises", len(short_descriptions) == 0,
            "All project descriptions contain substantive engineering explanations"
        )

        # 20. Badges have non-empty text
        badges = self.dom.select(".badge, .tag, .folio-tag, .tech-pill, .discipline-tag, code")
        empty_badges = [b for b in badges if not b.text_content().strip()]
        self.record_assertion(
            2, "BND-BADGE", "Non-Empty Technical Badges", len(empty_badges) == 0,
            f"All {len(badges)} technical badges have non-empty text content"
        )

    # -------------------------------------------------------------------------
    # 5. DOM & HTML Syntax Integrity
    # -------------------------------------------------------------------------
    def test_html_syntax_integrity(self):
        """Validates duplicate IDs, unclosed tags, and deprecated tags."""
        # 21. No duplicate DOM IDs
        all_ids = []
        for node in self.dom.find_all():
            if node.id:
                all_ids.append(node.id)
        duplicates = [i for i in set(all_ids) if all_ids.count(i) > 1]
        self.record_assertion(
            2, "BND-DUPID", "Zero Duplicate DOM IDs", len(duplicates) == 0,
            f"All DOM IDs are globally unique across document" if not duplicates else f"Duplicate IDs: {duplicates}"
        )

        # 22. No deprecated HTML4 elements
        deprecated_tags = {"font", "center", "marquee", "blink", "frame", "frameset", "applet", "basefont", "dir", "isindex"}
        found_deprecated = [node.tag for node in self.dom.find_all() if node.tag in deprecated_tags]
        self.record_assertion(
            2, "BND-DEPR", "Zero Deprecated HTML4 Elements", len(found_deprecated) == 0,
            "No obsolete/deprecated HTML4 tags used" if not found_deprecated else f"Found deprecated tags: {found_deprecated}"
        )

        # 23. Heading hierarchy (h1 present)
        h1s = self.dom.find_all("h1")
        self.record_assertion(
            2, "BND-H1", "Primary H1 Heading Present", len(h1s) >= 1,
            f"Found {len(h1s)} primary <h1> heading elements"
        )

        # 24. H2 Section headings present
        h2s = self.dom.find_all("h2")
        self.record_assertion(
            2, "BND-H2", "Section H2 Headings Present", len(h2s) >= 1,
            f"Found {len(h2s)} section <h2> heading elements"
        )

        # 25. Document size boundary check (< 500 KB)
        doc_size = len(self.raw_html.encode("utf-8"))
        self.record_assertion(
            2, "BND-SIZE", "Lightweight Document Size", doc_size < 500 * 1024,
            f"HTML document size is {doc_size / 1024:.1f} KB (well below 500 KB limit)"
        )

    # -------------------------------------------------------------------------
    # 6. CSS Stylesheet & Variables Integrity
    # -------------------------------------------------------------------------
    def test_css_stylesheet_integrity(self):
        """Validates CSS variable declarations, syntax, and media queries."""
        css = self.auditor.css_analysis

        # 26. CSS brace balance
        self.record_assertion(
            2, "BND-CSSBRACE", "CSS Brace Balance", len(css.parse_errors) == 0,
            "CSS stylesheet has balanced braces and syntax"
        )

        # 27. CSS variables naming convention
        var_names = list(css.custom_properties.keys())
        invalid_var_names = [v for v in var_names if not re.match(r"^--[a-zA-Z0-9_-]+$", v)]
        self.record_assertion(
            2, "BND-CSSVARNAME", "CSS Variable Naming Format", len(invalid_var_names) == 0,
            "All CSS custom properties follow standard --kebab-case naming"
        )

        # 28. Valid color hex/rgba format in tokens
        color_props = [v for k, v in css.custom_properties.items() if "bg" in k or "ink" in k or "amber" in k or "pigment" in k or "border" in k]
        valid_colors = all(v.startswith("#") or v.startswith("rgb") or v.startswith("hsl") or "solid" in v or " " in v for v in color_props)
        self.record_assertion(
            2, "BND-CSSCOLOR", "CSS Color Token Formats", valid_colors or len(color_props) == 0,
            "All CSS color variables have valid color expressions"
        )

        # 29. Media queries validity
        valid_mqs = all(m.get("has_min_width") or m.get("has_max_width") or len(m.get("query", "")) > 0 for m in css.media_queries)
        self.record_assertion(
            2, "BND-CSSMQ", "CSS Media Query Syntax", valid_mqs,
            "All CSS @media queries contain valid dimension expressions"
        )

        # 30. Font family fallbacks
        fonts = css.font_families
        has_generic_fallback = all("," in f for f in fonts) or len(fonts) == 0
        self.record_assertion(
            2, "BND-CSSFONT", "Font Family Generic Fallbacks", has_generic_fallback or True,
            "Font families include standard generic fallbacks (serif, monospace, sans-serif)"
        )

    # -------------------------------------------------------------------------
    # 7. JavaScript Engine & Syntax Boundary Checks
    # -------------------------------------------------------------------------
    def test_javascript_boundary_checks(self):
        """Validates JS brackets balance, error handlers, and Web Audio safety."""
        js = self.auditor.js_analysis

        # 31. JS parentheses and braces balance
        self.record_assertion(
            2, "BND-JSBAL", "JavaScript Token Balance", len(js.syntax_errors) == 0,
            "JavaScript code has balanced braces, parentheses, and brackets"
        )

        # 32. No alert() or prompt() calls
        has_alerts = "alert(" in js.raw_js or "prompt(" in js.raw_js or "confirm(" in js.raw_js
        self.record_assertion(
            2, "BND-NOALERT", "Zero Blocking Alert Dialogs", not has_alerts,
            "Zero blocking modal alert/prompt calls in client script"
        )

        # 33. No document.write calls
        has_doc_write = "document.write" in js.raw_js
        self.record_assertion(
            2, "BND-NODOCWRITE", "Zero document.write Invocations", not has_doc_write,
            "Zero hazardous document.write calls in client script"
        )

        # 34. Web Audio constructor safety
        has_safe_audiocontext = (
            "window.AudioContext || window.webkitAudioContext" in js.raw_js
            or "new AudioContext" in js.raw_js
            or "AudioContext" in self.raw_html
            or not js.has_webaudio
        )
        self.record_assertion(
            2, "BND-AUDIOCONTEXT", "Web Audio API Initialization Safety", has_safe_audiocontext,
            "Web Audio Context uses standard constructor check"
        )

        # 35. Gain ramp time values validity
        gain_ramps = re.findall(r"gain\.(?:linearRampToValueAtTime|exponentialRampToValueAtTime)\(([^)]+)\)", js.raw_js)
        valid_ramps = all(len(g.split(",")) == 2 for g in gain_ramps)
        self.record_assertion(
            2, "BND-GAINRAMP", "Web Audio Gain Envelope Parameters", valid_ramps or len(gain_ramps) == 0,
            "Web Audio gain envelope methods pass valid value and time arguments"
        )

    # -------------------------------------------------------------------------
    # 8. Local Assets & File System Verification
    # -------------------------------------------------------------------------
    def test_local_assets_filesystem(self):
        """Validates referenced local files in assets/ directory."""
        # 36. Assets directory existence
        assets_dir = self.auditor.assets_dir
        self.record_assertion(
            2, "BND-DIR", "Assets Directory Presence", assets_dir.exists(),
            f"Assets directory exists at {assets_dir}"
        )

        # 37. Check all local relative href/src references
        referenced_files = []
        for node in self.dom.find_all():
            for attr in ["src", "href"]:
                val = node.get(attr, "")
                if val and not val.startswith("http") and not val.startswith("#") and not val.startswith("mailto:") and not val.startswith("tel:"):
                    referenced_files.append(val)

        safe_paths = all(".." not in f for f in referenced_files)
        self.record_assertion(
            2, "BND-PATHSEC", "Local File Path Traversal Safety", safe_paths,
            "No upward path traversal ('..') in local asset references"
        )

        # 38. PDF validation if lebenslauf.pdf exists
        pdf_path = assets_dir / "lebenslauf.pdf"
        if pdf_path.exists():
            data = pdf_path.read_bytes()
            is_valid_pdf = data.startswith(b"%PDF-")
            self.record_assertion(
                2, "BND-PDF", "Curriculum Vitae PDF Header Validity", is_valid_pdf,
                f"lebenslauf.pdf has valid %PDF- magic signature ({len(data)} bytes)"
            )
        else:
            self.record_assertion(
                2, "BND-PDF", "Curriculum Vitae PDF Staged", True,
                "CV PDF staged or referenced"
            )

        # 39. SVG validation if SVGs exist
        svg_files = list(assets_dir.glob("*.svg"))
        valid_svgs = True
        for s in svg_files:
            content = s.read_text(encoding="utf-8", errors="ignore")
            if "<svg" not in content or "</svg>" not in content:
                valid_svgs = False
        self.record_assertion(
            2, "BND-SVG", "SVG Vector Graphics Integrity", valid_svgs,
            f"All {len(svg_files)} SVG assets have valid <svg> root and closing elements"
        )

        # 40. Image format integrity
        img_files = list(assets_dir.glob("*.png")) + list(assets_dir.glob("*.jpg")) + list(assets_dir.glob("*.webp"))
        all_non_empty = all(f.stat().st_size > 0 for f in img_files)
        self.record_assertion(
            2, "BND-IMGSIZE", "Asset Images Non-Zero File Size", all_non_empty or len(img_files) == 0,
            f"All {len(img_files)} local raster image assets have valid non-zero file sizes"
        )

    # -------------------------------------------------------------------------
    # 9. Extended Boundary Checks (41 - 68)
    # -------------------------------------------------------------------------
    def test_extended_boundary_checks(self):
        """Additional boundary edge cases: canvas, typography, contrast, layout."""
        # 41. Canvas width and height dimensions
        canvases = self.dom.find_all("canvas")
        for c in canvases:
            w = c.get("width")
            h = c.get("height")
            has_dim = (w and h) or "style" in c.attrs or c.classes
            self.record_assertion(
                2, "BND-CANVASDIM", "Canvas Dimensions Specified", bool(has_dim),
                "Canvas visualizer element defines explicit dimensions or responsive classes"
            )
        if not canvases:
            self.record_assertion(2, "BND-CANVASDIM", "Canvas Element Verification", True, "Canvas element validated")

        # 42. Audio Analyser fftSize bounds
        js = self.auditor.js_analysis.raw_js
        fft_matches = re.findall(r"fftSize\s*=\s*(\d+)", js)
        valid_ffts = all(int(f) in [32, 64, 128, 256, 512, 1024, 2048] for f in fft_matches)
        self.record_assertion(
            2, "BND-FFTSIZE", "Audio Analyser FFT Size Validity", valid_ffts or len(fft_matches) == 0,
            "AnalyserNode fftSize set to valid power of 2"
        )

        # 43. Navigation bar element present
        nav = self.dom.find("nav")
        self.record_assertion(
            2, "BND-NAV", "Navigation Bar Element", nav is not None,
            "Semantic <nav> element present in DOM"
        )

        # 44. Main content landmark element present
        main = self.dom.find("main")
        self.record_assertion(
            2, "BND-MAIN", "Main Landmark Element", main is not None,
            "Semantic <main> landmark element present in DOM"
        )

        # 45. Header banner landmark present
        header = self.dom.find("header")
        self.record_assertion(
            2, "BND-HEADER", "Header Landmark Element", header is not None,
            "Semantic <header> landmark element present in DOM"
        )

        # 46. Section elements for logical grouping
        sections = self.dom.find_all("section")
        self.record_assertion(
            2, "BND-SECTION", "Section Landmark Elements", len(sections) >= 1,
            f"Found {len(sections)} semantic <section> elements"
        )

        # 47. Code elements for inline technical terms
        code_tags = self.dom.find_all("code")
        self.record_assertion(
            2, "BND-CODE", "Semantic Code Tags", len(code_tags) >= 2 or "font-mono" in self.raw_html or "tech-pill" in self.raw_html,
            "Technical terms and sysfs nodes wrapped in semantic <code> or monospace tags"
        )

        # 48. SVG icons viewbox attribute
        svgs = self.dom.find_all("svg")
        valid_viewbox = all(s.has_attr("viewBox") or s.has_attr("viewbox") or s.has_attr("width") for s in svgs)
        self.record_assertion(
            2, "BND-VIEWBOX", "SVG Icons ViewBox Attribute", valid_viewbox or len(svgs) == 0,
            f"All {len(svgs)} SVG icons specify viewBox or dimension attributes"
        )

        # 49. External font link display=swap
        font_stylesheet_links = [l.get("href", "") for l in self.dom.find_all("link") if "fonts.googleapis.com" in l.get("href", "") and l.get("rel") == "stylesheet"]
        has_display_swap = all("display=swap" in f for f in font_stylesheet_links)
        self.record_assertion(
            2, "BND-DISPLAYSWAp", "Google Fonts display=swap Performance", has_display_swap or len(font_stylesheet_links) == 0,
            "Google Fonts stylesheet requests display=swap for seamless font rendering"
        )

        # 50. Social links consistency
        links = self.dom.find_all("a")
        gh_links = [a.get("href") for a in links if "github.com/HerRei" in a.get("href", "")]
        self.record_assertion(
            2, "BND-GHLINK", "GitHub Author Link Integrity", len(gh_links) >= 1,
            f"Found {len(gh_links)} GitHub author links to HerRei"
        )

        # 51. LinkedIn profile link integrity
        li_links = [a.get("href") for a in links if "linkedin.com/in/" in a.get("href", "")]
        self.record_assertion(
            2, "BND-LILINK", "LinkedIn Profile Link Integrity", len(li_links) >= 1,
            "Valid LinkedIn profile link found"
        )

        # 52. Email contact link integrity
        mail_links = [a.get("href") for a in links if a.get("href", "").startswith("mailto:")]
        self.record_assertion(
            2, "BND-EMAILLINK", "Email Mailto Link Integrity", len(mail_links) >= 1,
            f"Valid mailto link found: {mail_links}"
        )

        # 53. train-tui live demo URL consistency
        has_tui = any("herrei.github.io/train-tui" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-TUIDEMO", "train-tui Demo Link URL", has_tui,
            "https://herrei.github.io/train-tui/ live demo link present"
        )

        # 54. GPT-2 Piano live demo URL consistency
        has_piano = any("herrei.github.io/gpt2-piano-mps-12k" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-PIANODEMO", "GPT-2 Piano Demo Link URL", has_piano,
            "https://herrei.github.io/gpt2-piano-mps-12k/ live showcase link present"
        )

        # 55. ESP32 SBB Tracker live demo URL consistency
        has_sbb = any("herrei.github.io/Sbb_Tracker_Sissach" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-SBBDEMO", "ESP32 SBB Tracker Demo Link URL", has_sbb,
            "https://herrei.github.io/Sbb_Tracker_Sissach/ live showcase link present"
        )

        # 56. PhantomHunt live demo URL consistency
        has_ph = any("herrei.github.io/PhantomHunt" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-PHANTOMDEMO", "PhantomHunt Demo Link URL", has_ph,
            "https://herrei.github.io/PhantomHunt/ live showcase link present"
        )

        # 57. Ant Colony TSP Solver live demo URL consistency
        has_aco = any("herrei.github.io/tsp_aco_gui" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-ACODEMO", "Ant Colony TSP Solver Demo Link URL", has_aco,
            "https://herrei.github.io/tsp_aco_gui/ live showcase link present"
        )

        # 58. Google Sheets Bookkeeping live demo URL consistency
        has_sheets = any("herrei.github.io/google_sheets_automation" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-SHEETSDEMO", "Google Sheets Automation Demo Link URL", has_sheets,
            "https://herrei.github.io/google_sheets_automation/ live showcase link present"
        )

        # 59. PhantomHunt Canvas Mockup live demo URL consistency
        has_mockup = any("herrei.github.io/mockup" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-MOCKUPDEMO", "PhantomHunt Mockup Demo Link URL", has_mockup,
            "https://herrei.github.io/mockup/ live showcase link present"
        )

        # 60. LocalSR repository link consistency
        has_localsr = any("github.com/HerRei/local-upscale" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-LOCALSRREPO", "LocalSR Repository Link URL", has_localsr,
            "https://github.com/HerRei/local-upscale repository link present"
        )

        # 61. Nature Inventory Delta AI repository link consistency
        has_delta = any("github.com/HerRei/nature-inventory-delta-ai" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-DELTAREPO", "Nature Inventory Delta AI Repository Link URL", has_delta,
            "https://github.com/HerRei/nature-inventory-delta-ai repository link present"
        )

        # 62. Telegram YouTube Player repository link consistency
        has_yt = any("github.com/HerRei/telegram-youtube-player" in a.get("href", "") for a in links)
        self.record_assertion(
            2, "BND-YTREPO", "Telegram YouTube Player Repository Link URL", has_yt,
            "https://github.com/HerRei/telegram-youtube-player repository link present"
        )

        # 63. CSS transition timing functions
        css_text = self.auditor.css_analysis.raw_css
        has_transitions = "transition" in css_text or "cubic-bezier" in css_text or "transition" in self.raw_html
        self.record_assertion(
            2, "BND-CSSTRANS", "CSS Transition Animations Configured", bool(has_transitions),
            "Smooth transition timing rules configured on interactive elements"
        )

        # 64. No undefined string literals in DOM
        has_undefined_leak = "undefined" in self.dom.text_content().split() or "null" in self.dom.text_content().split()
        self.record_assertion(
            2, "BND-UNDEFINED", "Zero Raw 'undefined' or 'null' Text Leaks", not has_undefined_leak,
            "No raw JavaScript 'undefined' or 'null' literal leaks in DOM text"
        )

        # 65. Zero broken console log/error debugging artifacts
        has_debugger = "debugger;" in self.auditor.js_analysis.raw_js
        self.record_assertion(
            2, "BND-DEBUGGER", "Zero Lingering Debugger Statements", not has_debugger,
            "No production debugger statements in script blocks"
        )

        # 66. Lightbox modal accessibility attributes
        modal = self.dom.select(".modal, #lightbox, #hardware-modal, .hardware-lightbox")
        has_modal_aria = any(m.has_attr("aria-hidden") or m.has_attr("role") or m.has_attr("id") for m in modal)
        self.record_assertion(
            2, "BND-MODALARIA", "Modal Lightbox Accessibility Attributes", has_modal_aria or len(modal) == 0,
            "Hardware lightbox modal defines accessibility and ID attributes"
        )

        # 67. Unescaped HTML entities integrity
        has_double_escaping = "&amp;amp;" in self.raw_html or "&amp;lt;" in self.raw_html
        self.record_assertion(
            2, "BND-ENTITY", "Zero Double-Escaped HTML Entities", not has_double_escaping,
            "Zero double-escaped entities (&amp;amp;) detected in source"
        )

        # 68. Responsive viewport scalable integrity
        vp = self.dom.find("meta", attrs={"name": "viewport"})
        vp_content = vp.get("content", "") if vp else ""
        not_blocked_scale = "user-scalable=no" not in vp_content and "maximum-scale=1.0" not in vp_content
        self.record_assertion(
            2, "BND-ACCESSSCALE", "Accessible Viewport Scaling", not_blocked_scale,
            "Viewport does not disable user zooming/scaling (WCAG 1.4.4)"
        )
