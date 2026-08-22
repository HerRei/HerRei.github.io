# Project: HerRei.github.io Romantic-Era Classical Atelier Redesign

## Architecture
- **Architecture Type**: Pure Static Web Application (HTML5, CSS3, Vanilla JavaScript ES6+).
- **Zero Build Tools**: Direct browser execution, zero external runtime JS libraries, zero bundlers.
- **Design Philosophy**: 19th-century Romantic-Era Classical Atelier / Natural Philosopher Compendium. Chiaroscuro high-contrast dark palette, literary serifs (`EB Garamond` / `Cormorant Garamond`), technical monospace (`JetBrains Mono`), hairline etched borders, Roman numeral folios `[I]`–`[X]`, and botanical/astronomical glyph accents (`✦`, `§`, `❖`).
- **Interactive Engines**:
  - Web Audio API acoustic piano synthesizer with real-time `<canvas>` oscilloscope visualizer for GPT-2 Piano.
  - Live ANSI terminal telemetry stream for `train-tui` with interactive pause/resume.
  - Hardware plate with ST7789 TFT display simulation and expandable lightbox for ESP32 SBB Tracker.
  - Category filtering engine across 6 distinct domains with fluid opacity/transform transitions.
- **Directory Layout**:
  - `index.html`: Unified, standalone production portfolio page.
  - `assets/`: Bundled local media (personal portrait `profilbild.png`, curriculum vitae `lebenslauf.pdf`, ESP32 hardware graphics `board-closeup.svg`, `board-installed.svg`).
  - `tests/`: E2E opaque-box validation suite and test runner.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Romantic Atelier Design System | Dark obsidian palette (`#0a0b10`), parchment typography (`#f2ebe0`), candlelit amber (`#c89658`), etched borders, zero generic AI blobs | M1 | ORIGINAL_REQUEST §R1 |
| F2 | Literary Serif & Monospace Typography | Google Fonts `EB Garamond` / `Cormorant Garamond` paired with `JetBrains Mono` | M1 | ORIGINAL_REQUEST §R1 |
| F3 | Classical Foliation & Ornamentation | Roman numerals `[I]`–`[X]`, glyphs (`✦`, `§`, `❖`), etched card frames | M1 | ORIGINAL_REQUEST §R1 |
| F4 | 10-Project Compendium Plates | Full curation of all 10 projects with descriptions, tags, and badges | M2 | ORIGINAL_REQUEST §R2 |
| F5 | Instant Category Filtering | 6 categories: All, Systems & C, AI & ML, Embedded & IoT, Java & Distributed, Tools & Automation | M2 | ORIGINAL_REQUEST §R2 |
| F6 | Live Demo & GitHub Links | Verified working links to `github.com/HerRei/<repo>` and `herrei.github.io/<demo>` for all 10 projects | M2 | ORIGINAL_REQUEST §R2 |
| F7 | Bundled Assets & Media Integration | Local assets copied to `assets/` (portrait, CV PDF, ESP32 board illustrations) | M2 | ORIGINAL_REQUEST §R3 |
| F8 | Web Audio Piano Synthesizer | Zero-dependency Web Audio piano theme generator with animated oscilloscope | M3 | ORIGINAL_REQUEST §R3 |
| F9 | Live ANSI Terminal Simulator | Interactive sysfs telemetry monitor for `train-tui` (GPU, temp, power, VRAM) | M3 | ORIGINAL_REQUEST §R3 |
| F10 | ESP32 Hardware Showcase | SBB Tracker plate with live TFT UI preview and modal lightbox viewer | M3 | ORIGINAL_REQUEST §R3 |
| F11 | Academic Dossier & Contacts | University of Basel computer science profile, 4 engineering pillars, Email, GitHub, LinkedIn, CV download | M3 | ORIGINAL_REQUEST §R3 |
| F12 | Full Responsive Layout | Mobile (<768px), tablet (768-1024px), desktop (>1024px) seamless responsiveness | M4 | ORIGINAL_REQUEST §R4 |
| F13 | Zero-Error Static Quality & Git Deployment | Valid HTML5/CSS3/JS, zero console errors, committed & pushed to `main` | M4 | ORIGINAL_REQUEST §R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Atelier Visual System & Base Layout | CSS custom properties, typography, classical ornaments, header, banner, footer layout | none | IN_PROGRESS |
| M2 | Project Compendium & Asset Integration | Staging `assets/` (portrait, CV, hardware SVGs), 10 project plates `[I]`–`[X]`, 6-category filter logic | M1 | PLANNED |
| M3 | Interactive Micro-Engines & Academic Dossier | Web Audio piano synth + visualizer, ANSI terminal simulator, ESP32 lightbox modal, Uni Basel bio & contact links | M2 | PLANNED |
| M4 | E2E Verification, Responsive Polish & Git Push | Pass 100% E2E test suite, cross-device audit, zero console errors, git commit & push to `main` | M3, E2E | PLANNED |

## Code Layout
- `/Users/hermesheiniger/HerRei.github.io/index.html` — Main production portfolio application
- `/Users/hermesheiniger/HerRei.github.io/assets/` — Staged local assets (CV PDF, portrait, hardware SVGs)
- `/Users/hermesheiniger/HerRei.github.io/tests/` — Automated E2E verification test suite
