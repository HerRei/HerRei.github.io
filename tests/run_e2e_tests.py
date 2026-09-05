#!/usr/bin/env python3
"""Run the current portfolio content and interactive-engine assertions."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromNames([
        "tests.test_portfolio_content",
        "tests.test_adversarial_interactive_engines",
    ])
    result = unittest.TextTestRunner(verbosity=2 if "--verbose" in sys.argv else 1).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
