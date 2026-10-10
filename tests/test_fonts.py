"""Unit tests for typography font loading and fallbacks."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL.ImageFont import FreeTypeFont, ImageFont

import core.fonts as fonts_module
from core.fonts import FONTS_DIR, get_font


def test_fonts_dir_exists() -> None:
    """Ensure FONTS_DIR points to an existing directory with assets."""
    assert FONTS_DIR.is_dir()
    assert (FONTS_DIR / "DejaVuSans.ttf").is_file()
    assert (FONTS_DIR / "DejaVuSans-Bold.ttf").is_file()


def test_get_font_regular_returns_bundled_font() -> None:
    """Ensure get_font loads the bundled regular font with the requested size."""
    font = get_font(size=24, bold=False)
    assert isinstance(font, FreeTypeFont)
    assert font.size == 24


def test_get_font_bold_returns_bundled_font() -> None:
    """Ensure get_font loads the bold font with the requested size."""
    font = get_font(size=32, bold=True)
    assert isinstance(font, FreeTypeFont)
    assert font.size == 32


def test_get_font_fallback_when_path_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure get_font falls back to Pillow default font if assets missing."""
    monkeypatch.setattr(fonts_module, "FONTS_DIR", Path("/nonexistent"))
    font = get_font(size=20)
    assert isinstance(font, (FreeTypeFont, ImageFont))
