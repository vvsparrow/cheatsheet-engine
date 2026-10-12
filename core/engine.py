"""Rendering engine for cheatsheet wallpapers."""

from __future__ import annotations

import time
from pathlib import Path

from PIL import Image, ImageDraw

from core.fonts import get_font
from core.layout import calculate_page_capacity, calculate_page_layout
from core.models import TableData
from core.observability import MetricsCollector, RenderReport, get_logger
from core.presets import (
    IPAD_PORTRAIT,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
    DevicePreset,
)
from core.theme import DARK_THEME, Theme
from core.typography import truncate_to_width, wrap_text

logger = get_logger("cheatsheet")


def render_wallpaper(
    table: TableData,
    preset: DevicePreset,
    output_path: Path,
    page: int = 1,
    collector: MetricsCollector | None = None,
    theme: Theme = DARK_THEME,
) -> Path:
    """Render a cheatsheet wallpaper matching the given device preset geometry.

    Args:
        table: Tabular dataset to render.
        preset: Target device layout and resolution preset.
        output_path: Destination filesystem path for the rendered image.
        page: One-based page number for paginated rendering.
        collector: Optional metrics collector to capture execution report.

    Returns:
        Path to the generated image file.

    Raises:
        ValueError: If page is less than 1.
    """
    if page < 1:
        raise ValueError("Page number must be greater than or equal to 1.")

    start_time = time.perf_counter()
    layout = calculate_page_layout(table=table, preset=preset, page=page)

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
            page_index=page,
            total_pages=1,
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

    if preset == PHONE_PANORAMA:
        panel_w = preset.resolution.width // 3
        start_x = (panel_w - layout.single_block_width) // 2
    elif preset in (IPAD_PORTRAIT, PHONE_LOCKSCREEN):
        start_x = safe_area.x + (safe_area.width - total_content_w) // 2
    else:
        start_x = safe_area.right - total_content_w

    current_y = safe_area.y
    for block_idx in range(layout.num_blocks):
        block_x = start_x + block_idx * (layout.single_block_width + layout.gutter)
        current_y = safe_area.y

        col_x_offsets: list[int] = []
        curr_x = block_x
        for w in layout.single_widths:
            col_x_offsets.append(curr_x)
            curr_x += w

        for col_idx, header in enumerate(table.headers):
            fitted_header = truncate_to_width(
                text=header,
                font=header_font,
                max_width=max(10, layout.single_widths[col_idx] - 20),
            )
            draw.text(
                (col_x_offsets[col_idx], current_y),
                fitted_header,
                fill=theme.text_header,
                font=header_font,
            )

        current_y += 30
        draw.line(
            [(block_x, current_y), (block_x + layout.single_block_width, current_y)],
            fill=theme.separator,
            width=2,
        )
        current_y += 15

        b_start = block_idx * layout.rows_per_block
        b_end = b_start + layout.rows_per_block
        block_rows = layout.page_rows[b_start:b_end]

        for row_idx, row in enumerate(block_rows):
            row_lines = [
                wrap_text(
                    text=cell,
                    font=body_font,
                    max_width=max(10, layout.single_widths[col_idx] - 20),
                )
                for col_idx, cell in enumerate(row)
            ]
            num_lines = max((len(lines) for lines in row_lines), default=1)
            line_step = int(layout.font_size * 1.35)
            row_height = num_lines * line_step + 4

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
                            col_x_offsets[col_idx],
                            current_y + line_idx * line_step,
                        ),
                        line,
                        fill=theme.text_primary,
                        font=body_font,
                    )
            current_y += row_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    content_height = max(0, current_y - safe_area.y)
    safe_area_area = safe_area.width * safe_area.height
    utilization = (
        round((total_content_w * content_height) / safe_area_area, 4)
        if safe_area_area > 0
        else 0.0
    )

    page_capacity = calculate_page_capacity(table=table, preset=preset)
    total_pages = (
        max(1, (table.row_count + page_capacity - 1) // page_capacity)
        if page_capacity > 0
        else 1
    )

    report = RenderReport(
        preset_name=preset.name,
        page_index=page,
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
