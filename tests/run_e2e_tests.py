#!/usr/bin/env python3
"""
Comprehensive, Standalone E2E Test Suite Runner for HerRei.github.io Redesign.
Blends classical aesthetic verification with rigorous 4-Tier test architecture.

Usage:
    python3 tests/run_e2e_tests.py [--verbose] [--tier {1,2,3,4}] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_base import BaseE2ETestCase, TestResultItem
from tests.tier1_feature_coverage import TestTier1FeatureCoverage
from tests.tier2_boundary_corner import TestTier2BoundaryCorner
from tests.tier3_cross_feature import TestTier3CrossFeature
from tests.tier4_real_world_scenarios import TestTier4RealWorldScenarios


# ANSI Color Codes for Romantic Atelier Terminal Aesthetics
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_AMBER = "\033[38;2;200;150;88m"
C_GOLD = "\033[38;2;228;179;115m"
C_OBSIDIAN = "\033[38;2;142;131;113m"
C_PARCHMENT = "\033[38;2;242;235;224m"
C_GREEN = "\033[38;2;95;170;110m"
C_RED = "\033[38;2;210;75;75m"
C_CYAN = "\033[38;2;60;140;180m"
C_DIM = "\033[2m"


def print_banner():
    print(f"{C_AMBER}{C_BOLD}╔═══════════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_AMBER}{C_BOLD}║       HERMÈS REISNER · CATALOGUE OF WORKS · END-TO-END TEST RUNNER            ║{C_RESET}")
    print(f"{C_AMBER}{C_BOLD}║       Four tiers · features, boundaries, combinations, whole journeys         ║{C_RESET}")
    print(f"{C_AMBER}{C_BOLD}╚═══════════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")


def run_tier(tier_name: str, test_class: type, verbose: bool = False) -> Tuple_Results:
    print(f"{C_GOLD}{C_BOLD}▶ Executing {tier_name}...{C_RESET}")
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    
    start_time = time.perf_counter()
    result = runner.run(suite)
    elapsed = time.perf_counter() - start_time
    
    return result, elapsed


Tuple_Results = tuple


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    sep = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    lines = [sep]
    header_line = "│ " + " │ ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers)) + " │"
    lines.append(header_line)
    lines.append(mid)

    for row in rows:
        row_line = "│ " + " │ ".join(f"{str(v):<{col_widths[i]}}" for i, v in enumerate(row)) + " │"
        lines.append(row_line)
    lines.append(bot)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="HerRei.github.io E2E Test Suite Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose assertion details")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run a specific tier only")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON results")
    args = parser.parse_args()

    if not args.json:
        print_banner()

    tiers_to_run = [
        (1, "Tier 1: Feature coverage (F1 – F13)", TestTier1FeatureCoverage),
        (2, "Tier 2: Boundaries & corner cases", TestTier2BoundaryCorner),
        (3, "Tier 3: Feature combinations", TestTier3CrossFeature),
        (4, "Tier 4: Whole journeys", TestTier4RealWorldScenarios)
    ]

    if args.tier:
        tiers_to_run = [t for t in tiers_to_run if t[0] == args.tier]

    # Clear recorded results
    BaseE2ETestCase.collected_results.clear()

    total_start = time.perf_counter()
    tier_summaries = []
    has_failures = False

    for tier_num, tier_title, test_cls in tiers_to_run:
        before_count = len(BaseE2ETestCase.collected_results)
        res, elapsed = run_tier(tier_title, test_cls, args.verbose)
        after_count = len(BaseE2ETestCase.collected_results)
        
        tier_items = BaseE2ETestCase.collected_results[before_count:after_count]
        tier_passed = sum(1 for item in tier_items if item.passed)
        tier_failed = sum(1 for item in tier_items if not item.passed)

        if tier_failed > 0 or not res.wasSuccessful():
            has_failures = True

        status_str = f"{C_GREEN}PASS{C_RESET}" if tier_failed == 0 and res.wasSuccessful() else f"{C_RED}FAIL{C_RESET}"
        if not args.json:
            print(f"  └─ Status: {status_str} | Assertions: {tier_passed}/{len(tier_items)} passed | Time: {elapsed:.3f}s\n")
            if args.verbose:
                for item in tier_items:
                    mark = f"{C_GREEN}✓{C_RESET}" if item.passed else f"{C_RED}✗{C_RESET}"
                    print(f"     {mark} [{item.feature_id}] {item.name}: {item.message}")
                print()

        tier_summaries.append({
            "tier": tier_num,
            "title": tier_title,
            "passed": tier_passed,
            "failed": tier_failed,
            "total": len(tier_items),
            "elapsed": elapsed,
            "success": (tier_failed == 0 and res.wasSuccessful())
        })

    total_elapsed = time.perf_counter() - total_start
    total_assertions = len(BaseE2ETestCase.collected_results)
    total_passed = sum(1 for item in BaseE2ETestCase.collected_results if item.passed)
    total_failed = sum(1 for item in BaseE2ETestCase.collected_results if not item.passed)

    if args.json:
        json_output = {
            "summary": {
                "total_assertions": total_assertions,
                "passed": total_passed,
                "failed": total_failed,
                "success": not has_failures,
                "duration_seconds": round(total_elapsed, 4)
            },
            "tiers": tier_summaries,
            "results": [
                {
                    "tier": it.tier,
                    "feature_id": it.feature_id,
                    "name": it.name,
                    "passed": it.passed,
                    "message": it.message,
                    "details": it.details
                }
                for it in BaseE2ETestCase.collected_results
            ]
        }
        print(json.dumps(json_output, indent=2))
        sys.exit(0 if not has_failures else 1)

    # Print Summary Table
    headers = ["Tier", "Description", "Assertions", "Passed", "Failed", "Duration", "Status"]
    table_rows = []
    for s in tier_summaries:
        status_label = "PASS" if s["success"] else "FAIL"
        table_rows.append([
            f"Tier {s['tier']}",
            s["title"].split(":")[1].strip() if ":" in s["title"] else s["title"],
            str(s["total"]),
            str(s["passed"]),
            str(s["failed"]),
            f"{s['elapsed']:.3f}s",
            status_label
        ])
    
    print(f"\n{C_AMBER}{C_BOLD}═══ TEST EXECUTION SUMMARY ═══{C_RESET}")
    print(format_table(headers, table_rows))

    # Feature Checklist Matrix
    print(f"\n{C_GOLD}{C_BOLD}═══ 13-FEATURE VERIFICATION CHECKLIST ═══{C_RESET}")
    features = [
        ("F1", "Paper ground & pigments", "Warm laid paper, iron-gall ink, hairline rules, one vermillion"),
        ("F2", "Typography", "Bodoni Moda + EB Garamond + JetBrains Mono, old-style figures, drop cap"),
        ("F3", "The catalogue", "Ten works as wall labels: medium, date, where it is kept"),
        ("F4", "The index line", "Six filters whose tallies match what they will show"),
        ("F5", "Provenance", "Every work links to its repository or is declared private"),
        ("F6", "Specimens", "Telemetry readout, synthesised nocturne, departure panel"),
        ("F7", "Honest captions", "Figures declare what they are; colophon explains the dates"),
        ("F8", "Accessibility", "One h1, ordered headings, skip link, named sections, visible focus"),
        ("F9", "Responsive sheet", "Breakpoints, single-column entries, gutter preserved"),
        ("F10", "The print sheet", "Filters dropped, hidden entries restored, URLs spelled out"),
        ("F11", "Assets", "Everything referenced exists; nothing misattributed is published"),
        ("F12", "Restrained motion", "Reduced-motion honoured, ticker pauses in a hidden tab"),
        ("F13", "Architecture", "One file, one style block, one script, no third-party runtime"),
    ]

    f_headers = ["#", "Feature", "Specification", "Status"]
    f_rows = []
    for fid, fname, fspec in features:
        # Check if all Tier 1 assertions for this feature passed
        f_items = [it for it in BaseE2ETestCase.collected_results if it.feature_id == fid]
        f_passed = all(it.passed for it in f_items) if f_items else True
        f_status = "VERIFIED" if f_passed else "FAIL"
        f_rows.append([fid, fname, fspec, f_status])
    
    print(format_table(f_headers, f_rows))

    # Final Verdict
    print(f"\n{C_PARCHMENT}{C_BOLD}Total Assertions: {total_assertions} | Passed: {total_passed} | Failed: {total_failed} | Time: {total_elapsed:.3f}s{C_RESET}")
    if not has_failures:
        print(f"\n{C_GREEN}{C_BOLD}❧ All four tiers passed. The catalogue is ready to be impressed. ❧{C_RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{C_RED}{C_BOLD}✖ Failures detected. See the report above. ✖{C_RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
