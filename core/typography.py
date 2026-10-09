"""Defensive typography and text truncation utilities."""

from __future__ import annotations

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont


def truncate_to_width(
    text: str,
    font: FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
    ellipsis: str = "...",
) -> str:
    """Truncate text with an ellipsis if it exceeds the maximum pixel width.

    Args:
        text: Unput string to measure and truncate.
        font: Font instance used for pixel dimension calculation.
        max_width: Maximum allowed width in pixels.
        ellipsis: Trailing indicator string appended to truncated text.

    Returns:
        Original string if it fits, or truncated string with ellipsis.

    Raises:
        ValueError: If max_width is less than or equl to 0.
    """
    if max_width <= 0:
        raise ValueError("max_width must be strictly positive.")

    if not text:
        return ""

    bbox = font.getbbox(text)
    if (bbox[2] - bbox[0]) <= max_width:
        return text

    truncated = text
    while truncated:
        truncated = truncated[:-1]
        candidate = f"{truncated}{ellipsis}"
        cand_bbox = font.getbbox(candidate)
        if (cand_bbox[2] - cand_bbox[0]) <= max_width:
            return candidate

    ell_bbox = font.getbbox(ellipsis)
    if (ell_bbox[2] - ell_bbox[0]) <= max_width:
        return ellipsis
    return ""


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

        fitted_word = truncate_to_width(text=word, font=font, max_width=max_width)

        if not current_line:
            current_line = fitted_word
        else:
            candidate = f"{current_line} {fitted_word}"
            bbox = font.getbbox(candidate)
            if (bbox[2] - bbox[0]) <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = fitted_word

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
