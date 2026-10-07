"""Layout and rendering engine for cheatsheet wallpapers."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.models import TableData

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def get_font(size: int, bold: bool = False) -> FreeTypeFont | ImageFont.ImageFont:
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


def calculate_column_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    padding: int = 20,
) -> tuple[int, ...]:
    """Calculate dynamic column widths based on maximum text bounding boxes.

    Args:
        table: Tabular dataset with headers and rows.
        font: Font used to measure rendered text metrics.
        padding: Horizontal padding in pixels added to each column.

    Returns:
        Tuple of integer column widths in pixels.
    """
    widths: list[int] = []
    for col_idx in range(table.column_count):
        max_width = 0
        header_bbox = font.getbbox(table.headers[col_idx])
        header_width = header_bbox[2] - header_bbox[0]
        max_width = max(max_width, header_width)

        for row in table.rows:
            cell_bbox = font.getbbox(row[col_idx])
            cell_width = cell_bbox[2] - cell_bbox[0]
            max_width = max(max_width, cell_width)

        widths.append(int(max_width + padding))

    return tuple(widths)
