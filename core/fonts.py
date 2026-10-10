"""Font management and loading utilities for cheatsheet rendering."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def get_font(
    size: int,
    bold: bool = False,
) -> FreeTypeFont | ImageFont.ImageFont:
    """Load a bundled font by size and weight with fallback to default font.

    Args:
        size: Font point size.
        bold: Whether to load bold typeface weight.

    Returns:
        Loaded FreeTypeFont or Pillow fallback font.
    """
    font_name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    font_path = FONTS_DIR / font_name

    try:
        return ImageFont.truetype(str(font_path), size=size)
    except OSError:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()
