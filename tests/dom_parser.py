"""
Standalone DOM Parser and Query Engine for HTML5 documents.
Zero external dependencies — uses Python's standard library html.parser.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, Callable, Dict, List, Optional, Set


VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
}


class DOMNode:
    """Represents a single node in the parsed HTML document tree."""

    def __init__(self, tag: str, attrs: Optional[Dict[str, str]] = None, parent: Optional["DOMNode"] = None):
        self.tag = tag.lower() if tag else ""
        self.attrs = attrs or {}
        self.parent = parent
        self.children: List["DOMNode"] = []
        self.text_chunks: List[str] = []
        self.line_number = 0
        self.is_void = self.tag in VOID_TAGS

    @property
    def id(self) -> str:
        return self.attrs.get("id", "")

    @property
    def classes(self) -> Set[str]:
        cls = self.attrs.get("class", "")
        return set(cls.split()) if cls else set()

    def get(self, attr: str, default: Any = None) -> Any:
        return self.attrs.get(attr, default)

    def has_attr(self, attr: str) -> bool:
        return attr in self.attrs

    def has_class(self, class_name: str) -> bool:
        return class_name in self.classes

    def text_content(self, strip: bool = True) -> str:
        """Returns recursive text content of node and all children."""
        res: List[str] = []

        def _recurse(node: DOMNode):
            for chunk in node.text_chunks:
                if chunk:
                    res.append(chunk)
            for child in node.children:
                _recurse(child)

        _recurse(self)
        joined = " ".join(res)
        if strip:
            return re.sub(r"\s+", " ", joined).strip()
        return joined

    @property
    def inner_text(self) -> str:
        return self.text_content(strip=True)

    def find(self, tag: Optional[str] = None, attrs: Optional[Dict[str, Any]] = None, **kwargs) -> Optional["DOMNode"]:
        matches = self.find_all(tag=tag, attrs=attrs, limit=1, **kwargs)
        return matches[0] if matches else None

    def find_all(
        self,
        tag: Optional[str] = None,
        attrs: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> List["DOMNode"]:
        """Recursively finds all matching descendant DOM nodes."""
        results: List["DOMNode"] = []
        query_attrs = dict(attrs or {})
        query_attrs.update(kwargs)

        def _match(node: DOMNode) -> bool:
            if tag and tag != "*" and node.tag != tag.lower():
                return False
            for k, v in query_attrs.items():
                attr_name = "class" if k in ("class_", "cls") else k
                if attr_name not in node.attrs:
                    return False
                val = node.attrs[attr_name]
                if isinstance(v, (set, list, tuple)):
                    node_classes = node.classes
                    if not set(v).issubset(node_classes):
                        return False
                elif isinstance(v, re.Pattern):
                    if not v.search(val):
                        return False
                elif callable(v):
                    if not v(val):
                        return False
                elif val != str(v):
                    # Class special handling (token matching)
                    if attr_name == "class" and str(v) in node.classes:
                        continue
                    return False
            return True

        def _walk(node: DOMNode):
            if limit and len(results) >= limit:
                return
            for child in node.children:
                if _match(child):
                    results.append(child)
                    if limit and len(results) >= limit:
                        return
                _walk(child)

        _walk(self)
        return results

    def select(self, selector: str) -> List["DOMNode"]:
        """CSS Selector engine supporting tags, IDs, classes, attributes, and combinators."""
        selectors = [s.strip() for s in selector.split(",") if s.strip()]
        all_results: Set[DOMNode] = set()

        for sel in selectors:
            res = self._select_single(sel)
            all_results.update(res)

        # Preserve document order
        ordered: List[DOMNode] = []

        def _collect(n: DOMNode):
            if n in all_results and n not in ordered:
                ordered.append(n)
            for c in n.children:
                _collect(c)

        _collect(self)
        return ordered

    def _select_single(self, selector: str) -> List["DOMNode"]:
        parts = re.split(r"(\s*>\s*|\s+)", selector.strip())
        tokens = [p for p in parts if p.strip()]

        current_nodes = [self]
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == ">":
                i += 1
                if i < len(tokens):
                    child_matcher = tokens[i]
                    next_nodes: List[DOMNode] = []
                    for n in current_nodes:
                        for child in n.children:
                            if self._match_simple_selector(child, child_matcher):
                                next_nodes.append(child)
                    current_nodes = next_nodes
            else:
                # Descendant search
                next_nodes = []
                for n in current_nodes:
                    for descendant in n.find_all():
                        if self._match_simple_selector(descendant, tok):
                            if descendant not in next_nodes:
                                next_nodes.append(descendant)
                current_nodes = next_nodes
            i += 1

        return current_nodes

    def _match_simple_selector(self, node: DOMNode, sel: str) -> bool:
        # sel could be: tag#id.class1.class2[attr=val]
        pattern = r"^([a-zA-Z0-9_-]+|\*)?(#([a-zA-Z0-9_-]+))?((?:\.[a-zA-Z0-9_-]+)*)((?:\[[^\]]+\])*)$"
        m = re.match(pattern, sel.strip())
        if not m:
            return False

        tag, _, node_id, classes, attrs = m.groups()
        if tag and tag != "*" and node.tag != tag.lower():
            return False
        if node_id and node.id != node_id:
            return False
        if classes:
            req_classes = set(c for c in classes.split(".") if c)
            if not req_classes.issubset(node.classes):
                return False
        if attrs:
            attr_patterns = re.findall(r"\[([a-zA-Z0-9_-]+)(?:([~|^$*]?=)(['\"]?)(.*?)\3)?\]", attrs)
            for attr_name, op, _, expected in attr_patterns:
                if attr_name not in node.attrs:
                    return False
                if not op:
                    continue  # Just existence
                val = node.attrs[attr_name]
                if op == "=" and val != expected:
                    return False
                elif op == "*=" and expected not in val:
                    return False
                elif op == "^=" and not val.startswith(expected):
                    return False
                elif op == "$=" and not val.endswith(expected):
                    return False
                elif op == "~=" and expected not in val.split():
                    return False
        return True

    def __repr__(self) -> str:
        attrs_str = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        return f"<{self.tag} {attrs_str}>" if attrs_str else f"<{self.tag}>"


class DOMTreeBuilder(HTMLParser):
    """HTML Parser that constructs a DOMNode tree."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = DOMNode("document")
        self.current = self.root
        self.raw_elements: List[DOMNode] = []
        self.unclosed_tags: List[str] = []
        self.duplicate_ids: List[str] = []
        self.all_ids: Set[str] = set()

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        attr_dict = {k.lower(): v or "" for k, v in attrs}
        node = DOMNode(tag, attr_dict, parent=self.current)
        node.line_number = self.getpos()[0]
        self.current.children.append(node)
        self.raw_elements.append(node)

        # ID uniqueness check
        node_id = attr_dict.get("id")
        if node_id:
            if node_id in self.all_ids:
                self.duplicate_ids.append(node_id)
            self.all_ids.add(node_id)

        if not node.is_void:
            self.current = node

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in VOID_TAGS:
            return  # Void tags do not have end tags

        # Find matching open tag in ancestor chain
        temp = self.current
        while temp and temp != self.root and temp.tag != tag_lower:
            temp = temp.parent

        if temp and temp != self.root:
            self.current = temp.parent or self.root
        else:
            self.unclosed_tags.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]}")

    def handle_data(self, data: str):
        if self.current:
            self.current.text_chunks.append(data)

    def handle_comment(self, data: str):
        pass


def parse_html(html_content: str) -> DOMNode:
    """Parses HTML string and returns the root document DOMNode."""
    builder = DOMTreeBuilder()
    builder.feed(html_content)
    builder.close()
    return builder.root
