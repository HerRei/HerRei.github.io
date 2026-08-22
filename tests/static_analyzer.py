"""
Static CSS, JavaScript, and Asset Analyzer for HerRei.github.io.
Provides AST-like inspection and static verification without external dependencies.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse


def _strip_at_blocks(css: str) -> str:
    """Remove @media / @supports blocks, braces balanced, leaving top-level rules."""
    out = []
    i = 0
    while i < len(css):
        if css[i] == "@":
            head_end = css.find("{", i)
            if head_end == -1:
                break
            depth = 0
            j = head_end
            while j < len(css):
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            i = j + 1
            continue
        out.append(css[i])
        i += 1
    return "".join(out)


class CSSAnalysis:
    """Encapsulates parsed CSS stylesheet rules, custom properties, and media queries."""

    def __init__(self, raw_css: str):
        self.raw_css = raw_css
        self.custom_properties: Dict[str, str] = {}
        self.conditional_properties: Dict[str, List[str]] = {}
        self.media_queries: List[Dict[str, Any]] = []
        self.selectors: Set[str] = set()
        self.font_families: List[str] = []
        self.keyframes: List[str] = []
        self.parse_errors: List[str] = []
        self._parse()

    def _parse(self):
        # 1. Clean comments
        clean = re.sub(r"/\*.*?\*/", "", self.raw_css, flags=re.DOTALL)

        # 2. Check balanced braces
        open_braces = clean.count("{")
        close_braces = clean.count("}")
        if open_braces != close_braces:
            self.parse_errors.append(f"Unbalanced braces in CSS: {open_braces} open vs {close_braces} close")

        # 3. Extract :root custom properties.
        #    Only from top-level :root blocks — a :root inside @media print is an
        #    override for one medium, and folding it in here would report the
        #    printed palette as if it were the screen's.
        for block in re.findall(r":root\s*\{([^}]+)\}", _strip_at_blocks(clean), flags=re.DOTALL):
            props = re.findall(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", block)
            for name, val in props:
                self.custom_properties[name.strip()] = val.strip()

        # 3b. Conditional overrides, kept apart so tests can inspect them.
        for block in re.findall(r":root\s*\{([^}]+)\}", clean, flags=re.DOTALL):
            for name, val in re.findall(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", block):
                if self.custom_properties.get(name.strip()) != val.strip():
                    self.conditional_properties.setdefault(name.strip(), []).append(val.strip())

        # 4. Extract font-family rules
        fonts = re.findall(r"font-family\s*:\s*([^;]+);", clean, flags=re.IGNORECASE)
        for f in fonts:
            self.font_families.append(f.strip())

        # 5. Extract @media queries
        media_blocks = re.finditer(r"@media\s*([^{]+)\{((?:[^{}]*\{[^{}]*\})*)\s*\}", clean, flags=re.DOTALL)
        for m in media_blocks:
            query = m.group(1).strip()
            body = m.group(2).strip()
            self.media_queries.append({
                "query": query,
                "body": body,
                "has_min_width": "min-width" in query,
                "has_max_width": "max-width" in query
            })

        # 6. Extract @keyframes
        kf = re.findall(r"@keyframes\s+([a-zA-Z0-9_-]+)", clean)
        self.keyframes = list(kf)

        # 7. Extract class and ID selectors
        classes = re.findall(r"\.([a-zA-Z0-9_-]+)", clean)
        self.selectors.update(f".{c}" for c in classes)
        ids = re.findall(r"#([a-zA-Z0-9_-]+)", clean)
        self.selectors.update(f"#{i}" for i in ids)

    def get_variable(self, name: str) -> Optional[str]:
        return self.custom_properties.get(name)

    def has_variable(self, name: str) -> bool:
        return name in self.custom_properties


class JSAnalysis:
    """Encapsulates static JavaScript inspection, token analysis, and API presence checks."""

    def __init__(self, raw_js: str):
        self.raw_js = raw_js
        self.syntax_errors: List[str] = []
        self.function_names: Set[str] = set()
        self.class_names: Set[str] = set()
        self._analyze()

    def _analyze(self):
        # 1. Clean comments
        clean = re.sub(r"/\*.*?\*/", "", self.raw_js, flags=re.DOTALL)
        clean = re.sub(r"//.*$", "", clean, flags=re.MULTILINE)

        # 2. Check balanced braces, parentheses, and brackets
        pairs = [("{", "}"), ("(", ")"), ("[", "]")]
        for open_ch, close_ch in pairs:
            # Note: ignore chars inside quotes for basic balance check
            open_count = clean.count(open_ch)
            close_count = clean.count(close_ch)
            if open_count != close_count:
                self.syntax_errors.append(
                    f"Unbalanced '{open_ch}'/'{close_ch}': {open_count} vs {close_count}"
                )

        # 3. Extract function names
        funcs = re.findall(r"function\s+([a-zA-Z0-9_$]+)\s*\(", clean)
        self.function_names.update(funcs)
        arrow_funcs = re.findall(r"(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:\([^)]*\)|[a-zA-Z0-9_$]+)\s*=>", clean)
        self.function_names.update(arrow_funcs)

        # 4. Extract class names
        classes = re.findall(r"class\s+([a-zA-Z0-9_$]+)", clean)
        self.class_names.update(classes)

    @property
    def has_webaudio(self) -> bool:
        return bool(re.search(r"\b(AudioContext|webkitAudioContext)\b", self.raw_js))

    @property
    def has_oscillator(self) -> bool:
        return bool(re.search(r"\bcreateOscillator\b", self.raw_js))

    @property
    def has_gain_node(self) -> bool:
        return bool(re.search(r"\bcreateGain\b", self.raw_js))

    @property
    def has_analyser_node(self) -> bool:
        return bool(re.search(r"\bcreateAnalyser\b", self.raw_js))

    @property
    def has_biquad_filter(self) -> bool:
        return bool(re.search(r"\bcreateBiquadFilter\b", self.raw_js))

    @property
    def has_canvas_2d(self) -> bool:
        return bool(re.search(r"getContext\(\s*['\"]2d['\"]\s*\)", self.raw_js))

    @property
    def has_animation_frame(self) -> bool:
        return bool(re.search(r"\brequestAnimationFrame\b", self.raw_js))


class ProjectAuditor:
    """Orchestrates comprehensive static analysis of HTML, CSS, JS, and local assets."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.index_path = self.project_root / "index.html"
        self.assets_dir = self.project_root / "assets"
        self.html_content = ""
        self.css_analysis: Optional[CSSAnalysis] = None
        self.js_analysis: Optional[JSAnalysis] = None
        self._load()

    def _load(self):
        if self.index_path.exists():
            self.html_content = self.index_path.read_text(encoding="utf-8")

        # Extract all <style> contents
        style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", self.html_content, flags=re.DOTALL | re.IGNORECASE)
        combined_css = "\n".join(style_blocks)
        self.css_analysis = CSSAnalysis(combined_css)

        # Extract all inline <script> contents (excluding JSON/LD or external src)
        script_blocks = re.findall(r"<script(?![^>]*src=)[^>]*>(.*?)</script>", self.html_content, flags=re.DOTALL | re.IGNORECASE)
        combined_js = "\n".join(script_blocks)
        self.js_analysis = JSAnalysis(combined_js)

    def check_asset_exists(self, rel_path: str) -> Tuple[bool, int]:
        """Checks if asset exists relative to project root or assets dir."""
        clean_rel = rel_path.lstrip("./").lstrip("/")
        p1 = self.project_root / clean_rel
        p2 = self.assets_dir / clean_rel
        p3 = self.assets_dir / Path(clean_rel).name

        target = None
        if p1.exists() and p1.is_file():
            target = p1
        elif p2.exists() and p2.is_file():
            target = p2
        elif p3.exists() and p3.is_file():
            target = p3

        if target:
            return True, target.stat().st_size
        return False, 0
