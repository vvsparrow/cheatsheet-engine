"""Rendering engine for cheatsheet wallpapers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from core.fonts import get_font
from core.layout import calculate_column_widths, calculate_rows_per_page
from core.models import TableData
from core.presets import DevicePreset
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
    max_col_w = safe_area.width // table.column_count
    widths = calculate_column_widths(
        table=table,
        font=header_font,
        padding=40,
        max_column_width=max_col_w,
    )

    col_x_offsets: list[int] = []
    current_x = safe_area.x
    for width in widths:
        col_x_offsets.append(current_x)
        current_x += width

    current_y = safe_area.y

    for col_idx, header in enumerate(table.headers):
        fitted_header = truncate_to_width(
            text=header,
            font=header_font,
            max_width=max(10, widths[col_idx] - 40),
        )
        draw.text(
            (col_x_offsets[col_idx], current_y),
            fitted_header,
            fill=(100, 200, 255),
            font=header_font,
        )

    current_y += 30
    total_table_width = sum(widths)
    draw.line(
        [(safe_area.x, current_y), (safe_area.x + total_table_width, current_y)],
        fill=(100, 200, 255),
        width=2,
    )
    current_y += 15

    rows_per_page = calculate_rows_per_page(
        safe_area=safe_area,
        row_height=28,
        header_height=45,
    )
    if rows_per_page > 0:
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        visible_rows = table.rows[start_idx:end_idx]
    else:
        visible_rows = ()

    for row in visible_rows:
        row_lines = [
            wrap_text(
                text=cell,
                font=body_font,
                max_width=max(10, widths[col_idx] - 40),
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
                    (col_x_offsets[col_idx], current_y + line_idx * line_step),
                    line,
                    fill=(240, 240, 240),
                    font=body_font,
                )
        current_y += row_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path
