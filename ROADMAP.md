# Product Roadmap: cheatsheet-engine

## Milestone 1: Core Layout Engine (v0.1.0) — Released

- [X] Basic layout generation (Pillow)
- [X] Data-driven Layout Engine (Resolution, SafeZone, dynamic
  bounding box)
- [X] Out-of-the-box presets:
  - Desktop 2K (2560x1440, icon margin)
  - Laptop Full HD (1920x1080, 16:9 grid)
  - Tablet / iPad (2048x2732, 3:4 portrait)
  - Phone Panorama (3240x2412, 3 screens)
  - Phone Lockscreen (1290x2796, Safe Zone: top 32%, bottom 12%)
- [X] Engine Migration & Dynamic Layout:
  - Dynamic column widths (no hardcoded offsets)
  - Zero-clipping text wrapping and auto-scaling
  - Cross-platform font fallback

## Milestone 2: Quality Gates (v0.2.0) — Released

- [X] Automated test suite (Pytest)
- [X] Collision detection (text overlaps via font metrics)
- [X] Boundary & Safe Zone assertions
- [X] Defensive Layout (Word wrapping, text truncation with ellipsis)
- [X] Modularize engine architecture (extract font loader, SRP #20)
- [X] Dynamic typography sizing & multi-column row balancing (#28)
- [X] Device UI Mockup Overlays (status bar, notch, and dock framing)
- [X] Visual Regression Testing (Snapshot / pixel-diff assertions)
- [X] Structured Logging & Observability (render metrics, layout reports)
- [X] Cross-platform CI/CD Pipeline (GitHub Actions: Linux, macOS, Windows)
- [X] Changelog tracking (Keep a Changelog standard, CHANGELOG.md)
- [X] Dataset Quality Gates (duplicate checks, sort order, schema validation)

## Milestone 3: Developer CLI & Packaging (v0.3.0) — Released

- [X] Command-line interface (CLI) for headless batch rendering
- [X] Interactive preview mode with auto-reload on dataset change
- [X] Automated batch packager: bundle wallpapers by device series
- [X] Anki Deck Compiler (genanki): parallel export with nested subdecks

## Milestone 4: Theming & Accessibility Standards (v0.4.0) — Current Focus

- [ ] Theme Engine: ThemeConfig model with WCAG 2.1 AA/AAA contrast checks
- [ ] High-contrast OLED palette (pure black floor optimization)
- [ ] Starter seed datasets (English verbs, Git, Linux sysadmin commands)

## Milestone 5: Production Release & Extensibility (v1.0.0)

- [ ] Extensible dataset provider plugins (CSV, JSON, Markdown, SQLite)
- [ ] Web API microservice (FastAPI async rendering endpoint)
- [ ] Open-source contribution guidelines (CONTRIBUTING.md)
