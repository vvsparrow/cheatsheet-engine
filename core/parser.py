"""Argument parser specification and command-line input validators."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.presets import (
    A4_LANDSCAPE,
    A4_PORTRAIT,
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    DevicePreset,
)
from core.theme import THEMES

__all__ = [
    "PRESET_CHOICES",
    "create_parser",
    "parse_scale_factor",
]

PRESET_CHOICES: dict[str, DevicePreset] = {
    "a4_landscape": A4_LANDSCAPE,
    "a4_portrait": A4_PORTRAIT,
    "desktop_2k": DESKTOP_2K,
    "ipad_portrait": IPAD_PORTRAIT,
    "laptop_fhd": LAPTOP_FHD,
    "phone_lockscreen": PHONE_LOCKSCREEN,
}


def parse_scale_factor(val: str) -> float:
    """Parse percentage or multiplier string to a float scale factor."""
    clean = val.strip().rstrip("%")
    try:
        num = float(clean)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid scale '{val}'. Must be a number or percentage."
        ) from None

    if val.strip().startswith(("+", "-")):
        factor = 1.0 + (num / 100.0)
    elif num > 2.0:
        factor = num / 100.0
    else:
        factor = num

    if not (0.5 <= factor <= 2.0):
        raise argparse.ArgumentTypeError(
            f"Scale {factor:.2f} out of bounds. Must be between 0.5 and 2.0."
        )
    return factor


def create_parser() -> argparse.ArgumentParser:
    """Build and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="cheatsheet",
        description="Cheatsheet Engine: Headless wallpaper & Anki deck generator.",
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESET_CHOICES.keys()) + ["all"],
        default="all",
        help="Target device layout preset or 'all' for complete batch.",
    )
    parser.add_argument(
        "--scale",
        type=parse_scale_factor,
        default=1.0,
        help="Custom layout scale factor or percentage (e.g. -5, +10, 95%%, 0.95).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("screensavers"),
        help="Destination directory for generated wallpapers and decks.",
    )
    parser.add_argument(
        "--mockups",
        action="store_true",
        help="Generate simulated device UI mockup overlays alongside wallpapers.",
    )
    parser.add_argument(
        "--theme",
        choices=sorted(THEMES.keys()),
        default="dark",
        help="Color palette theme for rendered wallpapers.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Optional path to custom CSV dataset file.",
    )
    parser.add_argument(
        "--anki",
        action="store_true",
        help="Compile matching .apkg Anki flashcard deck alongside wallpapers.",
    )
    parser.add_argument(
        "--deck-name",
        type=str,
        default="Cheatsheet Deck",
        help="Custom title for the compiled Anki deck.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console progress output.",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch dataset file for changes and re-render automatically.",
    )
    parser.add_argument(
        "--bundle",
        action="store_true",
        help="Bundle rendered wallpapers and artifacts into a zip archive with manifest.",
    )
    parser.add_argument(
        "--bundle-name",
        type=str,
        default="Cheatsheet Bundle",
        help="Custom title for the distribution bundle.",
    )
    return parser
