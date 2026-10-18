"""Wallpaper rendering orchestration."""

from __future__ import annotations

import time
from pathlib import Path

from PIL import Image, ImageDraw

from core.fonts import get_font
from core.layout import calculate_page_layout
from core.metrics import (
    CELL_MIN_TEXT_WIDTH,
    CELL_PAD_X,
    CELL_PAD_X_TOTAL,
    HEADER_LINE_OFFSET_MIN,
    HEADER_SPACER_MIN,
    HEADER_SPACER_RATIO,
    LINE_STEP_RATIO,
    ROW_PAD_Y_MIN,
    ROW_PAD_Y_RATIO,
)
from core.models import TableData
from core.observability import MetricsCollector, RenderReport, get_logger
from core.presets import DevicePreset
from core.theme import DARK_THEME, Theme
from core.typography import wrap_text

logger = get_logger("cheatsheet")


def render_wallpaper(
    table: TableData,
    preset: DevicePreset,
    output_path: Path,
    start_idx: int = 0,
    page_index: int = 1,
    total_pages: int = 1,
    collector: MetricsCollector | None = None,
    theme: Theme = DARK_THEME,
) -> Path:
    """Render a single wallpaper page starting from the given row index.

    Args:
        table: Tabular dataset to render.
        preset: Target device layout and resolution preset.
        output_path: Destination filesystem path for the rendered image.
        start_idx: Zero-based index of the first data row to render.
        page_index: One-based page number for reporting.
        total_pages: Total pages expected for the series (for reporting).
        collector: Optional metrics collector to capture execution report.
        theme: Color palette and visual tokens used for rendering.

    Returns:
        Path to the generated image file.

    Raises:
        ValueError: If start_idx is negative or page_index is less than 1.
    """
    if start_idx < 0:
        raise ValueError("start_idx must be greater than or equal to 0.")
    if page_index < 1:
        raise ValueError("page_index must be greater than or equal to 1.")

    start_time = time.perf_counter()
    layout = calculate_page_layout(table=table, preset=preset, start_idx=start_idx)

    img = Image.new(
        mode="RGB",
        size=(preset.resolution.width, preset.resolution.height),
        color=theme.background,
    )

    if layout.rows_per_block <= 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        report = RenderReport(
            preset_name=preset.name,
            page_index=page_index,
            total_pages=total_pages,
            rows_processed=0,
            column_widths=layout.single_widths,
            safe_zone_utilization=0.0,
            duration_ms=duration_ms,
        )
        logger.info(report.summary())
        if collector is not None:
            collector.record(report)
        return output_path

    draw = ImageDraw.Draw(img)
    safe_area = preset.get_safe_area()
    header_font = get_font(size=layout.font_size, bold=True)
    body_font = get_font(size=layout.font_size, bold=False)

    total_content_w = (
        layout.num_blocks * layout.single_block_width
        + (layout.num_blocks - 1) * layout.gutter
    )

    if preset.alignment == "right":
        start_x = safe_area.right - total_content_w
    elif preset.alignment == "center":
        start_x = safe_area.x + (safe_area.width - total_content_w) // 2
    else:
        start_x = safe_area.x

    max_y = safe_area.y
    for block_idx in range(layout.num_blocks):
        block_x = start_x + block_idx * (layout.single_block_width + layout.gutter)
        current_y = safe_area.y

        col_x_offsets: list[int] = []
        curr_x = block_x
        for w in layout.single_widths:
            col_x_offsets.append(curr_x)
            curr_x += w

        for col_idx, header in enumerate(table.headers):
            draw.text(
                (col_x_offsets[col_idx] + CELL_PAD_X, current_y),
                header,
                fill=theme.text_header,
                font=header_font,
            )

        current_y += max(
            HEADER_LINE_OFFSET_MIN, int(layout.font_size * LINE_STEP_RATIO)
        )
        draw.line(
            [(block_x, current_y), (block_x + layout.single_block_width, current_y)],
            fill=theme.separator,
            width=2,
        )
        current_y += max(HEADER_SPACER_MIN, int(layout.font_size * HEADER_SPACER_RATIO))

        b_start = block_idx * layout.rows_per_block
        b_end = b_start + layout.rows_per_block
        block_rows = layout.page_rows[b_start:b_end]

        for row_idx, row in enumerate(block_rows):
            row_lines = [
                wrap_text(
                    text=cell,
                    font=body_font,
                    max_width=max(
                        CELL_MIN_TEXT_WIDTH,
                        layout.single_widths[col_idx] - CELL_PAD_X_TOTAL,
                    ),
                )
                for col_idx, cell in enumerate(row)
            ]
            num_lines = max((len(lines) for lines in row_lines), default=1)
            line_step = int(layout.font_size * LINE_STEP_RATIO)
            pad_y = max(ROW_PAD_Y_MIN, int(layout.font_size * ROW_PAD_Y_RATIO))
            row_height = num_lines * line_step + 2 * pad_y

            if row_idx % 2 == 1:
                draw.rectangle(
                    [
                        (block_x, current_y),
                        (
                            block_x + layout.single_block_width,
                            current_y + row_height,
                        ),
                    ],
                    fill=theme.row_alt,
                )

            for col_idx, lines in enumerate(row_lines):
                for line_idx, line in enumerate(lines):
                    if not line:
                        continue
                    draw.text(
                        (
                            col_x_offsets[col_idx] + CELL_PAD_X,
                            current_y + pad_y + line_idx * line_step,
                        ),
                        line,
                        fill=theme.text_primary,
                        font=body_font,
                    )
            current_y += row_height
            max_y = max(max_y, current_y)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    content_height = max(0, max_y - safe_area.y)
    safe_area_area = safe_area.width * safe_area.height
    utilization = (
        round((total_content_w * content_height) / safe_area_area, 4)
        if safe_area_area > 0
        else 0.0
    )

    report = RenderReport(
        preset_name=preset.name,
        page_index=page_index,
        total_pages=total_pages,
        rows_processed=len(layout.page_rows),
        column_widths=layout.single_widths,
        safe_zone_utilization=utilization,
        duration_ms=duration_ms,
    )
    logger.info(report.summary())
    if collector is not None:
        collector.record(report)

    return output_path
