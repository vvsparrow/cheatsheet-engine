"""Layout calculations and element bounding box generation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from core.columns import calculate_column_widths, calculate_rows_per_page
from core.fonts import get_font
from core.models import TableData
from core.presets import (
    PHONE_LOCKSCREEN,
    DevicePreset,
)
from core.typography import calculate_adaptive_font_size


@dataclass(frozen=True, slots=True)
class PageLayout:
    """Computed geometric layout matrix for a single page of content.

    Attributes:
        single_widths: Measured widths for columns in a single table block.
        single_block_width: Total horizontal width of a single table block.
        rows_per_block: Maximum vertical data rows that fit in one block.
        num_blocks: Number of horizontal column blocks rendered on this page.
        gutter: Horizontal spacing in pixels between adjacent column blocks.
        page_capacity: Total maximum rows this page layout can accommodate.
        page_rows: Subset of table data rows allocated to this page.
        font_size: Rendered typography size in points.
    """

    single_widths: tuple[int, ...]
    single_block_width: int
    rows_per_block: int
    num_blocks: int
    gutter: int
    page_capacity: int
    page_rows: Sequence[Sequence[str]]
    font_size: int = 18


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
    effective_font_size = preset.font_size

    if table.column_count <= 3 and table.row_count > 0:
        usable_h = safe_area.height - int(preset.font_size * 2.2)
        effective_font_size = calculate_adaptive_font_size(
            available_height=usable_h,
            row_count=table.row_count,
            base_font_size=preset.font_size,
        )

    header_font = get_font(size=effective_font_size, bold=True)
    body_font = get_font(size=effective_font_size, bold=False)

    target_width: int | None = None
    max_col_w = safe_area.width // max(1, table.column_count)

    single_widths = calculate_column_widths(
        table=table,
        font=body_font,
        header_font=header_font,
        padding=20,
        max_column_width=max_col_w,
        target_width=target_width,
    )
    single_block_width = sum(single_widths)
    header_height = int(effective_font_size * 2.2)
    effective_row_height = max(
        preset.row_height,
        int(effective_font_size * 1.55),
    )
    rows_per_block = calculate_rows_per_page(
        safe_area=safe_area,
        row_height=effective_row_height,
        header_height=header_height,
    )

    if rows_per_block <= 0:
        return PageLayout(
            single_widths=single_widths,
            single_block_width=single_block_width,
            rows_per_block=0,
            num_blocks=1,
            gutter=0,
            page_capacity=0,
            page_rows=(),
            font_size=effective_font_size,
        )

    min_gutter = 24
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

    if num_blocks > 1:
        gutter = 24
    else:
        gutter = 0

    if num_blocks > 1 and page_rows:
        rows_per_block = min(
            rows_per_block,
            max(1, (len(page_rows) + num_blocks - 1) // num_blocks),
        )

    return PageLayout(
        single_widths=single_widths,
        single_block_width=single_block_width,
        rows_per_block=rows_per_block,
        num_blocks=num_blocks,
        gutter=gutter,
        page_capacity=page_capacity,
        page_rows=page_rows,
        font_size=effective_font_size,
    )
