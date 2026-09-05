#!/usr/bin/env python3
"""Compatibility entry point for current structural portfolio checks."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_portfolio_content")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
