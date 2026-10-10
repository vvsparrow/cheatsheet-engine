"""Rendering engine for cheatsheet wallpapers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from core.fonts import get_font
from core.layout import calculate_page_capacity, calculate_page_layout
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

    layout = calculate_page_layout(table=table, preset=preset, page=page)

    img = Image.new(
        mode="RGB",
        size=(preset.resolution.width, preset.resolution.height),
        color=(18, 20, 24),
    )

    if layout.rows_per_block <= 0:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
        return output_path

    draw = ImageDraw.Draw(img)
    safe_area = preset.get_safe_area()
    header_font = get_font(size=20, bold=True)
    body_font = get_font(size=18, bold=False)

    for block_idx in range(layout.num_blocks):
        block_x = safe_area.x + block_idx * (layout.single_block_width + layout.gutter)
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
                max_width=max(10, layout.single_widths[col_idx] - 40),
            )
            draw.text(
                (col_x_offsets[col_idx], current_y),
                fitted_header,
                fill=(100, 200, 255),
                font=header_font,
            )

        current_y += 30
        draw.line(
            [(block_x, current_y), (block_x + layout.single_block_width, current_y)],
            fill=(100, 200, 255),
            width=2,
        )
        current_y += 15

        b_start = block_idx * layout.rows_per_block
        b_end = b_start + layout.rows_per_block
        block_rows = layout.page_rows[b_start:b_end]

        for row in block_rows:
            row_lines = [
                wrap_text(
                    text=cell,
                    font=body_font,
                    max_width=max(10, layout.single_widths[col_idx] - 40),
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


def render_card_pack(
    table: TableData,
    preset: DevicePreset,
    output_dir: Path,
) -> tuple[Path, ...]:
    """Render complete paginated series of wallpapers for the dataset.

    Args:
        table: Tabular dataset to render across multiple pages.
        preset: Target device layout and resolution preset.
        output_dir: Destination directory for the generated card series.

    Returns:
        Tuple of filesystem Paths to the generated images in order.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    page_capacity = calculate_page_capacity(table=table, preset=preset)
    if page_capacity <= 0 or table.row_count == 0:
        slug = preset.name.lower().replace(" ", "_")
        single_path = output_dir / f"{slug}_part_1_of_1.png"
        render_wallpaper(
            table=table,
            preset=preset,
            output_path=single_path,
            page=1,
        )
        return (single_path,)

    total_pages = max(1, (table.row_count + page_capacity - 1) // page_capacity)
    slug = preset.name.lower().replace(" ", "_")
    paths: list[Path] = []

    for page in range(1, total_pages + 1):
        card_name = f"{slug}_part_{page}_of_{total_pages}.png"
        card_path = output_dir / card_name
        render_wallpaper(
            table=table,
            preset=preset,
            output_path=card_path,
            page=page,
        )
        paths.append(card_path)

    return tuple(paths)
