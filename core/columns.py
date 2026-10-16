"""Column measurement and safe area row allocation."""

from __future__ import annotations

from collections.abc import Sequence

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.metrics import (
    CELL_MIN_TEXT_WIDTH,
    CELL_PAD_X_TOTAL,
    LINE_STEP_RATIO,
    ROW_PAD_Y_MIN,
    ROW_PAD_Y_RATIO,
)
from core.models import BoundingBox, TableData
from core.typography import wrap_text


def calculate_column_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    header_font: FreeTypeFont | ImageFont.ImageFont | None = None,
    padding: int = CELL_PAD_X_TOTAL,
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


def calculate_column_min_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    header_font: FreeTypeFont | ImageFont.ImageFont | None = None,
    padding: int = CELL_PAD_X_TOTAL,
) -> tuple[int, ...]:
    """Calculate minimum column widths based on longest words and headers.

    Args:
        table: Tabular dataset with headers and rows.
        font: Font used to measure cell word text metrics.
        header_font: Font used to measure table header row text metrics.
        padding: Horizontal padding in pixels added to each column.

    Returns:
        Tuple of integer minimum column widths in pixels.
    """
    min_widths: list[int] = []
    h_font = header_font if header_font is not None else font
    for col_idx in range(table.column_count):
        h_bbox = h_font.getbbox(table.headers[col_idx])
        max_token_w = h_bbox[2] - h_bbox[0]
        for row in table.rows:
            cell_text = row[col_idx]
            for word in cell_text.split(" "):
                if word:
                    w_bbox = font.getbbox(word)
                    max_token_w = max(max_token_w, w_bbox[2] - w_bbox[0])
        min_widths.append(int(max_token_w + padding))
    return tuple(min_widths)


def fit_column_widths_to_boundary(
    natural_widths: Sequence[int],
    min_widths: Sequence[int],
    available_width: int,
) -> tuple[int, ...]:
    """Fit column widths within available width preserving minimum word bounds.

    Args:
        natural_widths: Natural unwrapped width for each column.
        min_widths: Absolute minimum width required by words and headers.
        available_width: Target bounding width to constrain columns.

    Returns:
        Tuple of integer column widths fitting within available width.
    """
    if not natural_widths:
        return ()

    total_natural = sum(natural_widths)
    if total_natural <= available_width:
        return tuple(natural_widths)

    total_min = sum(min_widths)
    if total_min >= available_width:
        return tuple(min_widths)

    excess = total_natural - available_width
    compressible = [
        max(0, nat - min_w) for nat, min_w in zip(natural_widths, min_widths)
    ]
    total_comp = sum(compressible)
    if total_comp == 0:
        return tuple(min_widths)

    reductions = [int(excess * comp / total_comp) for comp in compressible]
    allocated = [nat - red for nat, red in zip(natural_widths, reductions)]

    remainder = available_width - sum(allocated)
    for i in range(len(allocated) - 1, -1, -1):
        if remainder == 0:
            break
        if compressible[i] > 0:
            allocated[i] += remainder
            break

    return tuple(allocated)


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


def calculate_row_rendered_height(
    row: Sequence[str],
    font: FreeTypeFont | ImageFont.ImageFont,
    column_widths: tuple[int, ...],
    font_size: int,
) -> int:
    """Calculate the rendered pixel height of a data row with wrapped text.

    Args:
        row: Sequence of cell text values in the row.
        font: Font used to measure rendered text metrics.
        column_widths: Measured column widths for the row.
        font_size: Rendered font point size.

    Returns:
        Integer pixel height of the row including internal padding.
    """
    line_step = int(font_size * LINE_STEP_RATIO)
    pad_y = max(ROW_PAD_Y_MIN, int(font_size * ROW_PAD_Y_RATIO))
    num_lines = 1
    for col_idx, cell in enumerate(row):
        col_w = column_widths[col_idx] if col_idx < len(column_widths) else 100
        lines = wrap_text(
            text=cell,
            font=font,
            max_width=max(CELL_MIN_TEXT_WIDTH, col_w - CELL_PAD_X_TOTAL),
        )
        num_lines = max(num_lines, len(lines))
    return num_lines * line_step + 2 * pad_y


def calculate_dynamic_rows_per_block(
    rows: Sequence[Sequence[str]],
    font: FreeTypeFont | ImageFont.ImageFont,
    column_widths: tuple[int, ...],
    font_size: int,
    available_height: int,
    max_rows: int,
) -> int:
    """Calculate max rows fitting in height considering dynamic wrapping.

    Args:
        rows: Sequence of table rows to evaluate.
        font: Font used to measure wrapped text.
        column_widths: Measured column widths for the rows.
        font_size: Rendered typography size in points.
        available_height: Available vertical pixels for rows.
        max_rows: Initial upper bound for rows based on single-line height.

    Returns:
        Integer count of rows that fit without overflowing available_height.
    """
    if not rows or available_height <= 0 or max_rows <= 0:
        return max(0, max_rows)

    accumulated_height = 0
    count = 0
    for row in rows[:max_rows]:
        h = calculate_row_rendered_height(
            row=row,
            font=font,
            column_widths=column_widths,
            font_size=font_size,
        )
        if accumulated_height + h > available_height:
            break
        accumulated_height += h
        count += 1

    return max(1, count)
