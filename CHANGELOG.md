# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Quality Gates: collision detection (`assert_no_collisions`) and safe area boundary assertions.
- Defensive Layout: multi-line text wrapping and width truncation with ellipsis.
- Device Mockup Overlays: automatic drawing of status bars, notches, and dock framing.
- Visual Regression Testing: pixel-diff snapshot comparison using RMS threshold.
- Observability: structured logging and render metrics telemetry (`RenderReport`).
- CI/CD: cross-platform GitHub Actions matrix testing across Linux, macOS, and Windows.
- Dataset Validation: strict schema checks, duplicate detection, and alphabetical sort enforcement.

### Changed
- Modularized core engine architecture to separate font loading and layout generation.
- Synchronized dynamic typography sizing, column gutters, and multi-column row balancing.

## [0.1.0] - 2026-10-10

### Added
- Core layout generation engine using Pillow.
- Data-driven layout domain models (`Resolution`, `SafeZone`, `BoundingBox`).
- Five primary device presets: Desktop 2K, Laptop FHD, iPad Portrait, Phone Panorama, Phone Lockscreen.
- Dynamic column widths avoiding hardcoded offsets.
- Cross-platform TrueType font fallback mechanism.
- Initial irregular verbs seed dataset.
