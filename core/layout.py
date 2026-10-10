"""Layout calculations and element bounding box generation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.fonts import get_font
from core.models import BoundingBox, TableData
from core.presets import (
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
    DevicePreset,
)


@dataclass(frozen=True, slots=True)
class PageLayout:
    """Computed geometric layout matrix for a single page of content.

    Attributes:
        single_widths: Measured widths for columns in a single table block.
        single_block_width: Total horizontal width of a single table block.
        rows_per_block: Maximum vertical data rows that fit in one block.
        num_blocks: Number of horizontal column blocks rendered on this page.
        gutter: Horizontal spacing in pixels between adjacent column blocks.
        page_rows: Subset of table data rows allocated to this page.
    """

    single_widths: tuple[int, ...]
    single_block_width: int
    rows_per_block: int
    num_blocks: int
    gutter: int
    page_capacity: int
    page_rows: Sequence[Sequence[str]]


def calculate_column_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    padding: int = 20,
    max_column_width: int | None = None,
    target_width: int | None = None,
) -> tuple[int, ...]:
    """Calculate dynamic column widths based on maximum text bounding boxes.

    Args:
        table: Tabular dataset with headers and rows.
        font: Font used to measure rendered text metrics.
        padding: Horizontal padding in pixels added to each column.
        max_column_width: Optional upper bound constraint for column width.
        target_width: Optional width in pixels to stretch columns to.

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


def calculate_page_capacity(
    table: TableData,
    preset: DevicePreset,
) -> int:
    """Calculate the total row capacity across all column blocks on one page.

    Args:
        table: Tabular dataset with headers and rows.
        preset: Target device layout and resolution preset.

    Returns:
        Integer count of rows that fit into one page.
    """
    layout = calculate_page_layout(table=table, preset=preset, page=1)
    return layout.page_capacity


def calculate_page_layout(
    table: TableData,
    preset: DevicePreset,
    page: int = 1,
) -> PageLayout:
    """Calculate the layout grid parameters and rows for a specific page.

    Args:
        table: Tabular dataset with headers and rows.
        preset: Target device layout and resolution preset.
        page: One-based page number.

    Returns:
        PageLayout instance containing widths, blocks, and row slices.

    Raises:
        ValueError: If page is less than 1.
    """
    if page < 1:
        raise ValueError("Page number must be greater than or equal to 1.")

    safe_area = preset.get_safe_area()
    header_font = get_font(size=20, bold=True)

    target_width: int | None = None
    max_col_w: int | None = safe_area.width // max(1, table.column_count)
    if preset == PHONE_LOCKSCREEN:
        target_width = safe_area.width
        max_col_w = None

    single_widths = calculate_column_widths(
        table=table,
        font=header_font,
        padding=40,
        max_column_width=max_col_w,
        target_width=target_width,
    )
    single_block_width = sum(single_widths)

    rows_per_block = calculate_rows_per_page(
        safe_area=safe_area,
        row_height=28,
        header_height=45,
    )
    if rows_per_block <= 0:
        page_capacity = 0
        return PageLayout(
            page_capacity=page_capacity,
            single_widths=single_widths,
            single_block_width=single_block_width,
            rows_per_block=0,
            num_blocks=1,
            gutter=0,
            page_rows=(),
        )

    min_gutter = 40
    if preset == PHONE_LOCKSCREEN or single_block_width >= safe_area.width:
        max_blocks = 1
    else:
        max_blocks = max(
            1,
            (safe_area.width + min_gutter) // max(1, single_block_width + min_gutter),
        )

    page_capacity = rows_per_block * max_blocks
    start_idx = (page - 1) * page_capacity
    end_idx = start_idx + page_capacity
    page_rows = table.rows[start_idx:end_idx]

    if not page_rows:
        num_blocks = 1
    else:
        needed = (len(page_rows) + rows_per_block - 1) // rows_per_block
        num_blocks = max(1, min(max_blocks, needed))

    if preset == PHONE_PANORAMA:
        num_blocks = 3
        panel_w = preset.resolution.width // 3
        gutter = panel_w - single_block_width
        if page_rows:
            rows_per_block = min(
                rows_per_block,
                max(1, (len(page_rows) + 2) // 3),
            )
    elif num_blocks > 1:
        gutter = (safe_area.width - num_blocks * single_block_width) // (num_blocks - 1)
    else:
        gutter = 0

    return PageLayout(
        single_widths=single_widths,
        single_block_width=single_block_width,
        rows_per_block=rows_per_block,
        num_blocks=num_blocks,
        gutter=gutter,
        page_capacity=page_capacity,
        page_rows=page_rows,
    )
