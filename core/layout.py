"""Layout calculations and element bounding box generation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from core.columns import (
    calculate_column_min_widths,
    calculate_column_widths,
    calculate_dynamic_rows_per_block,
    calculate_rows_per_page,
    fit_column_widths_to_boundary,
)
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
        page_capacity: Total rows allocated to this page (len of page_rows).
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


def calculate_page_layout(
    table: TableData,
    preset: DevicePreset,
    start_idx: int = 0,
) -> PageLayout:
    """Calculate the layout grid parameters and rows from a start index.

    Args:
        table: Tabular dataset with headers and rows.
        preset: Target device layout and resolution preset.
        start_idx: Zero-based index of the first data row to render.

    Returns:
        PageLayout instance containing widths, blocks, and row slices.

    Raises:
        ValueError: If start_idx is negative.
    """
    if start_idx < 0:
        raise ValueError("start_idx must be greater than or equal to 0.")

    safe_area = preset.get_safe_area()
    effective_font_size = preset.font_size

    if table.row_count > 0:
        usable_h = safe_area.height - int(preset.font_size * 2.2)
        candidate_size = calculate_adaptive_font_size(
            available_height=usable_h,
            row_count=table.row_count,
            base_font_size=preset.font_size,
        )
        while candidate_size > preset.font_size:
            cand_widths = calculate_column_widths(
                table=table,
                font=get_font(size=candidate_size, bold=False),
                header_font=get_font(size=candidate_size, bold=True),
                padding=20,
            )
            if sum(cand_widths) <= safe_area.width:
                effective_font_size = candidate_size
                break
            candidate_size -= 1

    header_font = get_font(size=effective_font_size, bold=True)
    body_font = get_font(size=effective_font_size, bold=False)

    natural_widths = calculate_column_widths(
        table=table,
        font=body_font,
        header_font=header_font,
        padding=20,
    )
    min_widths = calculate_column_min_widths(
        table=table,
        font=body_font,
        header_font=header_font,
        padding=20,
    )
    single_widths = fit_column_widths_to_boundary(
        natural_widths=natural_widths,
        min_widths=min_widths,
        available_width=safe_area.width,
    )
    single_block_width = sum(single_widths)
    header_height = max(30, int(effective_font_size * 1.2)) + max(
        15, int(effective_font_size * 0.5)
    )
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

    rough_capacity = rows_per_block * max_blocks
    page_rows = table.rows[start_idx : start_idx + rough_capacity]

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
    available_body_height = max(0, safe_area.height - header_height)
    if page_rows:
        dyn_limit = rows_per_block
        for b in range(num_blocks):
            b_rows = page_rows[b * rows_per_block : (b + 1) * rows_per_block]
            if not b_rows:
                break
            b_fit = calculate_dynamic_rows_per_block(
                rows=b_rows,
                font=body_font,
                column_widths=single_widths,
                font_size=effective_font_size,
                available_height=available_body_height,
                max_rows=rows_per_block,
            )
            dyn_limit = min(dyn_limit, b_fit)

        if dyn_limit < rows_per_block:
            rows_per_block = max(1, dyn_limit)
            page_rows = table.rows[start_idx : start_idx + rows_per_block * num_blocks]

    return PageLayout(
        single_widths=single_widths,
        single_block_width=single_block_width,
        rows_per_block=rows_per_block,
        num_blocks=num_blocks,
        gutter=gutter,
        page_capacity=len(page_rows),
        page_rows=page_rows,
        font_size=effective_font_size,
    )
