"""Rendering engine for cheatsheet wallpapers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from core.fonts import get_font
from core.layout import calculate_column_widths, calculate_rows_per_page
from core.models import TableData
from core.presets import PHONE_LOCKSCREEN, DevicePreset
from core.typography import truncate_to_width, wrap_text


def render_wallpaper(
    table: TableData,
    preset: DevicePreset,
    output_path: Path,
    page: int = 1,
) -> Path:
    """Render a cheatsheet wallpaper matching the given device preset geometry.

    Args:
        table: Tabular dataset to render.
        preset: Target device layout and resolution preset.
        output_path: Destination filesystem path for the rendered image.
        page: One-based page number for paginated rendering.

    Returns:
        Path to the generated image file.

    Raises:
        ValueError: If page is less than 1.
    """
    if page < 1:
        raise ValueError("Page number must be greater than or equal to 1.")

    img = Image.new(
        mode="RGB",
        size=(preset.resolution.width, preset.resolution.height),
        color=(18, 20, 24),
    )

    draw = ImageDraw.Draw(img)
    safe_area = preset.get_safe_area()

    header_font = get_font(size=20, bold=True)
    body_font = get_font(size=18, bold=False)

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
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        return output_path

    min_gutter = 40
    if preset == PHONE_LOCKSCREEN or single_block_width >= safe_area.width:
        max_blocks = 1
    else:
        max_blocks = max(
            1,
            (safe_area.width + min_gutter) // max(1, single_block_width + min_gutter),
        )

    page_capacity = rows_per_block * max_blocks
    start_row_idx = (page - 1) * page_capacity
    end_row_idx = start_row_idx + page_capacity
    page_rows = table.rows[start_row_idx:end_row_idx]

    if not page_rows:
        num_blocks = 1
    else:
        needed_blocks = (len(page_rows) + rows_per_block - 1) // rows_per_block
        num_blocks = max(1, min(max_blocks, needed_blocks))

    gutter = (
        (safe_area.width - num_blocks * single_block_width) // (num_blocks - 1)
        if num_blocks > 1
        else 0
    )

    for block_idx in range(num_blocks):
        block_x = safe_area.x + block_idx * (single_block_width + gutter)
        current_y = safe_area.y

        col_x_offsets: list[int] = []
        curr_x = block_x
        for w in single_widths:
            col_x_offsets.append(curr_x)
            curr_x += w

        for col_idx, header in enumerate(table.headers):
            fitted_header = truncate_to_width(
                text=header,
                font=header_font,
                max_width=max(10, single_widths[col_idx] - 40),
            )
            draw.text(
                (col_x_offsets[col_idx], current_y),
                fitted_header,
                fill=(100, 200, 255),
                font=header_font,
            )

        current_y += 30
        draw.line(
            [(block_x, current_y), (block_x + single_block_width, current_y)],
            fill=(100, 200, 255),
            width=2,
        )
        current_y += 15

        b_start = block_idx * rows_per_block
        b_end = b_start + rows_per_block
        block_rows = page_rows[b_start:b_end]

        for row in block_rows:
            row_lines = [
                wrap_text(
                    text=cell,
                    font=body_font,
                    max_width=max(10, single_widths[col_idx] - 40),
                )
                for col_idx, cell in enumerate(row)
            ]
            num_lines = max((len(lines) for lines in row_lines), default=1)
            line_step = 24
            row_height = num_lines * line_step + 4

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
                        fill=(240, 240, 240),
                        font=body_font,
                    )
            current_y += row_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path
