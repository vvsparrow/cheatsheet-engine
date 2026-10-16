"""Defensive typography and text wrapping utilities."""

from __future__ import annotations

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.metrics import (
    DEFAULT_ADAPTIVE_LINE_RATIO,
    DEFAULT_MAX_FONT_SIZE,
)


def _split_indivisible_word(
    word: str,
    font: FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    """Split an overflowing indivisible word character-by-character."""
    chunks: list[str] = []
    current = ""
    for char in word:
        candidate = current + char
        bbox = font.getbbox(candidate)
        if (bbox[2] - bbox[0]) <= max_width or not current:
            current = candidate
        else:
            chunks.append(current)
            current = char
    if current:
        chunks.append(current)
    return chunks


def wrap_text(
    text: str,
    font: FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> tuple[str, ...]:
    """Dynamically wrap text within maximum pixel width boundaries.

    Args:
        text: Input string to wrap across lines.
        font: Font instance used for measuring dimensions.
        max_width: Maximum allowed width in pixels per line.

    Returns:
        Tuple of strings representing individual lines.

    Raises:
        ValueError: If max_width is less than or equal to 0.
    """
    if max_width <= 0:
        raise ValueError("max_width must be strictly positive.")

    if not text:
        return ("",)

    words = text.split(" ")
    lines: list[str] = []
    current_line = ""

    for word in words:
        if not word:
            continue

        candidate = f"{current_line} {word}" if current_line else word
        bbox = font.getbbox(candidate)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = candidate
            continue

        if current_line:
            lines.append(current_line)
            current_line = ""

        word_bbox = font.getbbox(word)
        if (word_bbox[2] - word_bbox[0]) <= max_width:
            current_line = word
        else:
            chunks = _split_indivisible_word(
                word=word,
                font=font,
                max_width=max_width,
            )
            lines.extend(chunks[:-1])
            current_line = chunks[-1]

    if current_line:
        lines.append(current_line)

    return tuple(lines) if lines else ("",)


def calculate_line_height(
    font: FreeTypeFont | ImageFont.ImageFont,
    line_spacing: int = 4,
) -> int:
    """Calculate the total line height including vertical spacing.

    Args:
        font: Font instance used to measure text height.
        line_spacing: Vertical spacing in pixels added between lines.

    Returns:
        Integer line height in pixels.

    Raises:
        ValueError: If line_spacing is negative.
    """
    if line_spacing < 0:
        raise ValueError("line_spacing must be non-negative.")

    bbox = font.getbbox("Hg")
    text_height = max(1, bbox[3] - bbox[1])
    return int(text_height + line_spacing)


def calculate_adaptive_font_size(
    available_height: int,
    row_count: int,
    base_font_size: int,
    max_font_size: int = DEFAULT_MAX_FONT_SIZE,
    line_height_ratio: float = DEFAULT_ADAPTIVE_LINE_RATIO,
) -> int:
    """Calculate adaptive font size scaling within aesthetic ergonomic bounds.

    Args:
        available_height: Usable vertical height in pixels.
        row_count: Number of table rows to fit vertically.
        base_font_size: Minimum baseline font size from preset geometry.
        max_font_size: Maximum upper bound font size limit.
        line_height_ratio: Vertical line-height factor relative to font size.

    Returns:
        Integer font size clamped within [base_font_size, max_font_size].
    """
    if available_height <= 0 or row_count <= 0 or base_font_size <= 0:
        return base_font_size

    height_per_row = available_height / row_count
    fitted_size = int(height_per_row / line_height_ratio)

    return max(base_font_size, min(max_font_size, fitted_size))
