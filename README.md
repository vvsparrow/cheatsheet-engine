# cheatsheet-engine

<p>
  <a href="https://sparrowlab.dev">
    <img src="assets/sparrow.svg" width="18" height="18" valign="middle" alt="SparrowLab" />
    <strong>sparrowlab.dev</strong>
  </a>
  • Personal SDET & Automation Laboratory
</p>

A multi-device wallpaper and cheatsheet pack generator built with Python and Pillow. Transforms structured datasets into pixel-perfect reference wallpapers tailored for monitors, tablets, and smartphones.

---

## Features

- **Multi-Device Layouts**:
  - **Desktop 2K (2560x1440)**: Built-in left margin preserving space for desktop icons.
  - **Laptop Full HD (1920x1080)**: Compact grid for standard 16:9 displays.
  - **Tablet / iPad (2048x2732)**: Balanced 4:3 multi-column layout.
  - **Phone Home Screen Panorama (3240x2412)**: 3-screen panoramic layout supporting horizontal wallpaper scroll.
  - **Phone Lockscreen Safe Zone (1290x2796)**: Content fitted into the safe zone below clock widgets (top 38%) and above navigation bars (bottom 15%).
- **Automated Typography**: Dynamic line heights, column offsets, and header separators.
- **Product Ready**: Generates a complete cross-device study pack in a single execution.

---

## Quick Start

### Prerequisites

- [uv](https://github.com/astral-sh/uv)
- Python 3.13+

### Run Generation

Clone the repository and generate the wallpaper bundle:

```bash
uv run python main.py
```

Generated assets are placed into the `screensavers/` directory.

---

## Tech Stack

- **Python 3.13+**
- **Pillow (PIL)** — Image rendering and typography layout
- **uv** — Fast dependency and environment management
