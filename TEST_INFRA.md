# E2E Test Infra: HerRei.github.io Redesign

## Test Philosophy
- Opaque-box, requirement-driven testing. Validates exact structural, functional, visual, accessibility, and link requirements without coupling to internal variable names.
- Methodology: 4-Tier verification (Tier 1: Feature Coverage, Tier 2: Boundary & Corner Cases, Tier 3: Cross-Feature Interactions, Tier 4: Real-World Workload Scenarios).

## Feature Inventory & Test Mapping
| # | Feature | Requirement | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|-------------|:------:|:------:|:------:|:------:|
| F1 | Romantic Atelier Aesthetic | R1 (Palette, borders, dark theme) | 5 | 5 | ✓ | ✓ |
| F2 | Typography Hierarchy | R1 (EB/Cormorant Garamond + JetBrains Mono) | 5 | 5 | ✓ | ✓ |
| F3 | Classical Ornamentation | R1 (Etched borders, `[I]`–`[X]`, glyphs `✦`, `§`, `❖`) | 5 | 5 | ✓ | ✓ |
| F4 | 10-Project Compendium | R2 (All 10 project plates present & rendered) | 5 | 5 | ✓ | ✓ |
| F5 | 6 Category Filters | R2 (All, Systems, AI, Embedded, Java, Automation) | 5 | 5 | ✓ | ✓ |
| F6 | Live Demo & GitHub Links | R2 (20 valid links across 10 projects) | 5 | 5 | ✓ | ✓ |
| F7 | Staged Media & Assets | R3 (Portrait, CV PDF, ESP32 SVGs exist & link) | 5 | 5 | ✓ | ✓ |
| F8 | Web Audio Piano Synthesizer | R3 (AudioContext, synth notes, canvas visualizer) | 5 | 5 | ✓ | ✓ |
| F9 | Live ANSI Terminal Simulator | R3 (`train-tui` telemetry, pause/resume button) | 5 | 5 | ✓ | ✓ |
| F10 | ESP32 Hardware Showcase | R3 (ST7789 TFT display markup, modal trigger) | 5 | 5 | ✓ | ✓ |
| F11 | Academic Dossier & Contacts | R3 (Uni Basel, 4 pillars, Email, LinkedIn, GitHub) | 5 | 5 | ✓ | ✓ |
| F12 | Responsive Layout | R4 (Mobile viewport, tablet, desktop CSS media queries) | 5 | 5 | ✓ | ✓ |
| F13 | Static Architecture & Zero Runtime Errors | R4 (Valid HTML5, clean CSS, zero JS errors) | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test Suite Runner: Python 3 with `BeautifulSoup4` / `urllib` / regex / static JS validation (`python3 tests/run_e2e_tests.py`).
- Pass/Fail Semantics: Exit code 0 indicates 100% test pass across all 4 tiers.
- Coverage Minimums:
  - Tier 1: ≥ 65 test cases (≥5 per feature × 13 features)
  - Tier 2: ≥ 65 test cases (boundary and edge cases)
  - Tier 3: ≥ 13 cross-feature combination tests
  - Tier 4: ≥ 8 end-to-end user application scenarios
  - Total Target: ≥ 150 automated verification assertions.
