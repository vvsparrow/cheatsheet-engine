"""Column measurement and safe area row allocation."""

from __future__ import annotations

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.models import BoundingBox, TableData


def calculate_column_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    header_font: FreeTypeFont | ImageFont.ImageFont | None = None,
    padding: int = 20,
    max_column_width: int | None = None,
    target_width: int | None = None,
) -> tuple[int, ...]:
    """Calculate dynamic column widths based on maximum text bounding boxes.

    Args:
        table: Tabular dataset with headers and rows.
        font: Font used to measure rendered text metrics.
        header_font: Font used to measure table header row text metrics.
        padding: Horizontal padding in pixels added to each column.
        max_column_width: Optional upper bound constraint for column width.
        target_width: Optional width in pixels to stretch columns to.

    Returns:
        Tuple of integer column widths in pixels.
    """
    widths: list[int] = []
    h_font = header_font if header_font is not None else font
    for col_idx in range(table.column_count):
        max_width = 0
        header_bbox = h_font.getbbox(table.headers[col_idx])
        header_width = header_bbox[2] - header_bbox[0]
        max_width = max(max_width, header_width)

        for row in table.rows:
            cell_bbox = font.getbbox(row[col_idx])
            cell_width = cell_bbox[2] - cell_bbox[0]
            max_width = max(max_width, cell_width)
        col_w = int(max_width + padding)
        if max_column_width is not None and max_column_width > 0:
            col_w = min(col_w, max_column_width)
        widths.append(col_w)
    if target_width is not None and target_width > 0 and widths:
        total_w = sum(widths)
        if 0 < total_w < target_width:
            scale = target_width / total_w
            scaled_widths = [int(w * scale) for w in widths]
            remainder = target_width - sum(scaled_widths)
            scaled_widths[-1] += remainder
            widths = scaled_widths
        elif total_w == 0:
            base_w = target_width // len(widths)
            scaled_widths = [base_w] * len(widths)
            remainder = target_width - sum(scaled_widths)
            scaled_widths[-1] += remainder
            widths = scaled_widths

    return tuple(widths)


def calculate_rows_per_page(
    safe_area: BoundingBox,
    row_height: int = 28,
    header_height: int = 45,
) -> int:
    """Calculate maximum table rows that fit within safe area height.

    Args:
        safe_area: Usable content bounding box.
        row_height: Height allocated for each data row in pixels.
        header_height: Height reserved for table header and separator.

    Returns:
        Integer count of rows that fit into the available height.
    """
    usable_height = safe_area.height - header_height
    if usable_height <= 0:
        return 0
    return usable_height // row_height
