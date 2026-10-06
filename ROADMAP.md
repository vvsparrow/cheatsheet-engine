# Product Roadmap: cheatsheet-engine

## Milestone 1: Core Layout Engine (v0.1.0) — Current Focus

- [x] Basic layout generation (Pillow)
- [X] Data-driven Layout Engine (Resolution, SafeZone, dynamic
  bounding box)
- [ ] Out-of-the-box presets:
  - Desktop 2K (2560x1440, icon margin)
  - Laptop Full HD (1920x1080, 16:9 grid)
  - Tablet / iPad (2048x2732, 3:4 portrait)
  - Phone Panorama (3240x2412, 3 screens)
  - Phone Lockscreen (1290x2796, Safe Zone: top 38%, bottom 15%)

## Milestone 2: Quality Gates (v0.2.0)

- [ ] Automated test suite (Pytest)
- [ ] Collision detection (text overlaps via font metrics)
- [ ] Boundary & Safe Zone assertions

## Milestone 3: Standalone Operator Tool (v0.3.0)

- [ ] Standalone build (.exe for Windows) for operator generation
  workflow

## Milestone 4: First Commercial Release (v1.0.0)

- [ ] First public release pack on Gumroad / Lemon Squeezy
- [ ] Preset themes (Classic Dark / Light)

## Milestone 5: Aesthetics & Wearables (v1.1.0)

- [ ] **Night Shift Mode**: High-contrast OLED dark palette for night
  clinicals
- [ ] **Apple Watch Micro-Cards**: Compact layouts for 41mm/45mm faces
  (GCS scale, IV drip rates)

## Milestone 6: Clinical Physical Reference (v1.2.0)

- [ ] **Badge Buddies**: Printable 300 DPI pocket cards for hospital
  badge holders

## Milestone 7: Niche Medical Expansion (v1.3.0)

- [ ] High-yield NCLEX specialized packs (Pediatrics, Pharmacology,
  Critical Care)
- [ ] Custom order CLI generator
