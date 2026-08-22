"""
Base Assertion Engine and Test Case Framework for E2E Suite.
Provides dual compatibility: runs seamlessly with standard unittest and custom runner.
"""

import os
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional
from tests.dom_parser import DOMNode, parse_html
from tests.static_analyzer import ProjectAuditor


class TestResultItem:
    """Represents a single assertion or test verification record."""

    def __init__(
        self,
        tier: int,
        feature_id: str,
        name: str,
        passed: bool,
        message: str = "",
        details: str = ""
    ):
        self.tier = tier
        self.feature_id = feature_id
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] Tier {self.tier} ({self.feature_id}) {self.name}: {self.message}"


class BaseE2ETestCase(unittest.TestCase):
    """Base test class providing DOM inspection, static auditor, and assertion tracking."""

    project_root: Path = Path("/Users/hermesheiniger/HerRei.github.io").resolve()
    dom: Optional[DOMNode] = None
    auditor: Optional[ProjectAuditor] = None
    raw_html: str = ""
    collected_results: List[TestResultItem] = []

    @classmethod
    def setUpClass(cls):
        index_file = cls.project_root / "index.html"
        if index_file.exists():
            cls.raw_html = index_file.read_text(encoding="utf-8")
            cls.dom = parse_html(cls.raw_html)
        else:
            cls.raw_html = ""
            cls.dom = parse_html("<html><body></body></html>")
        cls.auditor = ProjectAuditor(str(cls.project_root))

    def record_assertion(
        self,
        tier: int,
        feature_id: str,
        name: str,
        passed: bool,
        message: str = "",
        details: str = ""
    ):
        item = TestResultItem(tier, feature_id, name, passed, message, details)
        BaseE2ETestCase.collected_results.append(item)
        if not passed:
            self.fail(f"Assertion Failed: [{feature_id}] {name} - {message}\nDetails: {details}")

    def assert_contains_text(self, text: str, node: Optional[DOMNode], name: str, tier: int, fid: str):
        if not node:
            self.record_assertion(tier, fid, name, False, f"DOM node not found for text check: '{text}'")
            return
        content = node.text_content()
        passed = text.lower() in content.lower()
        self.record_assertion(
            tier, fid, name, passed,
            f"Expected text '{text}' in node <{node.tag}>" if not passed else f"Found text '{text}'",
            f"Node content: {content[:120]}..."
        )

    def assert_css_variable(self, var_name: str, tier: int, fid: str, expected_pattern: Optional[str] = None):
        val = self.auditor.css_analysis.get_variable(var_name)
        passed = val is not None
        if passed and expected_pattern:
            import re
            passed = bool(re.search(expected_pattern, val, re.IGNORECASE))
        self.record_assertion(
            tier, fid, f"CSS Var {var_name}", passed,
            f"CSS custom property '{var_name}' = '{val}'" if passed else f"Missing CSS var '{var_name}'"
        )
