"""Unit tests for defensive typography, word wrapping, wrapping, and text
truncation."""

from __future__ import annotations

import pytest
from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.engine import get_font
from core.typography import calculate_line_height, truncate_to_width, wrap_text


@pytest.fixture
def test_font() -> FreeTypeFont | ImageFont.ImageFont:
    """Provide standard DejaVu regular font for typography tests."""
    return get_font(size=18, bold=False)


def test_truncate_to_width_text_fits_returns_unchanged(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure text fitting within maximum width is returned unchanged."""
    text = "Short text"
    bbox = test_font.getbbox(text)
    text_width = int(bbox[2] - bbox[0])

    result = truncate_to_width(text=text, font=test_font, max_width=text_width + 50)
    assert result == text


def test_truncate_to_width_overflowing_text_appends_ellipsis(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure overflowing single-word text is truncated with an ellipsis."""
    text = "Supercalifragilisticexpialidocious"
    bbox = test_font.getbbox(text)
    full_width = int(bbox[2] - bbox[0])
    constrained_width = full_width // 2

    result = truncate_to_width(text=text, font=test_font, max_width=constrained_width)

    assert result.endswith("...")
    res_bbox = test_font.getbbox(result)
    res_width = res_bbox[2] - res_bbox[0]
    assert res_width <= constrained_width


def test_truncate_to_width_empty_string_returns_empty(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure empty string returns empty string without error."""
    result = truncate_to_width(text="", font=test_font, max_width=100)
    assert result == ""


def test_truncate_to_width_invalid_max_width_raises_value_error(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure non-positive max_width raises ValueError."""
    with pytest.raises(ValueError, match="max_width must be strictly positive"):
        truncate_to_width(text="test", font=test_font, max_width=0)


def test_truncate_to_width_handles_unicode(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure unicode text is truncated gracefully within width bounds."""
    text = "ПриветМирСпутниковаяСвязьТелекоммуникации"
    bbox = test_font.getbbox(text)
    full_width = int(bbox[2] - bbox[0])
    constrained_width = full_width // 3

    result = truncate_to_width(text=text, font=test_font, max_width=constrained_width)
    assert result.endswith("...")
    res_bbox = test_font.getbbox(result)
    assert res_bbox[2] - res_bbox[0] <= constrained_width


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


def test_wrap_text_truncates_overflowing_single_word(
    test_font: FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Ensure overflowing single word is truncated with ellipsis."""
    text = "Supercalifragilisticexpialidocious"
    max_width = 100

    lines = wrap_text(text=text, font=test_font, max_width=max_width)
    assert len(lines) == 1
    assert lines[0].endswith("...")
    bbox = test_font.getbbox(lines[0])
    assert bbox[2] - bbox[0] <= max_width


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
