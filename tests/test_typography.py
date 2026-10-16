"""Unit tests for defensive typography, word wrapping, wrapping, and text
truncation."""

from __future__ import annotations

import pytest
from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.engine import get_font
from core.typography import (
    calculate_adaptive_font_size,
    calculate_line_height,
    wrap_text,
)


@pytest.fixture
def test_font() -> FreeTypeFont | ImageFont.ImageFont:
    """Provide standard DejaVu regular font for typography tests."""
    return get_font(size=18, bold=False)


def test_wrap_text_fits_returns_single_line(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure text fitting within max_width returns single-item tuple."""
    text = "Short command"
    result = wrap_text(text=text, font=test_font, max_width=400)
    assert result == (text,)


def test_wrap_text_wraps_multi_word_phrase(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure multi-word phrase is wrapped into multiple lines within width."""
    text = "Show working tree status and list all untracked files"
    max_width = 150

    lines = wrap_text(text=text, font=test_font, max_width=max_width)
    assert len(lines) > 1

    for line in lines:
        bbox = test_font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        assert line_width <= max_width


def test_wrap_text_hard_wraps_overflowing_single_word(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure overflowing single word is hard-wrapped without ellipsis."""
    text = "Supercalifragilisticexpialidocious"
    max_width = 100

    lines = wrap_text(text=text, font=test_font, max_width=max_width)
    assert len(lines) > 1
    assert "".join(lines) == text
    assert not any("..." in line for line in lines)
    for line in lines:
        bbox = test_font.getbbox(line)
        assert (bbox[2] - bbox[0]) <= max_width or len(line) == 1


def test_wrap_text_hard_wraps_overflowing_unicode_word(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure overflowing unicode word is hard-wrapped without data loss."""
    text = "ПриветМирСпутниковаяСвязьТелекоммуникации"
    max_width = 120

    lines = wrap_text(text=text, font=test_font, max_width=max_width)
    assert len(lines) > 1
    assert "".join(lines) == text
    assert not any("..." in line for line in lines)


def test_wrap_text_handles_narrow_boundary_gracefully(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure word is preserved character-by-character on narrow boundary."""
    text = "Hi"
    max_width = 1

    lines = wrap_text(text=text, font=test_font, max_width=max_width)
    assert "".join(lines) == text
    assert len(lines) == 2


def test_wrap_text_empty_string_returns_empty_tuple(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure empty string returns tuple containing single empty string."""
    result = wrap_text(text="", font=test_font, max_width=200)
    assert result == ("",)


def test_wrap_text_invalid_max_width_raises_value_error(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure non-positive max_width raises ValueError."""
    with pytest.raises(ValueError, match="max_width must be strictly positive"):
        wrap_text(text="test", font=test_font, max_width=0)


def test_calculate_line_height_positive_and_scales_with_spacing(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure line height is strictly positive and increases with line spacing."""
    height_default = calculate_line_height(font=test_font)
    height_spaced = calculate_line_height(font=test_font, line_spacing=10)

    assert height_default > 0
    assert height_spaced == height_default + 6  # 10 - default 4 = +6


def test_calculate_line_height_invalid_spacing_raises_value_error(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure negative line spacing raises ValueError."""
    with pytest.raises(ValueError, match="line_spacing must be non-negative"):
        calculate_line_height(font=test_font, line_spacing=-1)


def test_calculate_adaptive_font_size_scales_up_for_few_rows() -> None:
    """Ensure font scales up towards max limit when few rows allow it."""
    font_size = calculate_adaptive_font_size(
        available_height=1200,
        row_count=25,
        base_font_size=18,
        max_font_size=24,
    )
    assert font_size == 24


def test_calculate_adaptive_font_size_caps_at_base_for_dense_rows() -> None:
    """Ensure font size does not shrink below base for dense datasets."""
    font_size = calculate_adaptive_font_size(
        available_height=1000,
        row_count=100,
        base_font_size=18,
        max_font_size=24,
    )
    assert font_size == 18


def test_calculate_adaptive_font_size_handles_edge_cases() -> None:
    """Ensure zero or negative inputs safely fall back to base font size."""
    assert (
        calculate_adaptive_font_size(
            available_height=0,
            row_count=25,
            base_font_size=18,
        )
        == 18
    )
    assert (
        calculate_adaptive_font_size(
            available_height=1000,
            row_count=0,
            base_font_size=18,
        )
        == 18
    )
