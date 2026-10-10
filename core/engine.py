"""Layout and rendering engine for cheatsheet wallpapers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from core.fonts import get_font
from core.models import BoundingBox, TableData
from core.presets import DevicePreset
from core.typography import truncate_to_width, wrap_text


def calculate_column_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    padding: int = 20,
    max_column_width: int | None = None,
) -> tuple[int, ...]:
    """Calculate dynamic column widths based on maximum text bounding boxes.

    Args:
        table: Tabular dataset with headers and rows.
        font: Font used to measure rendered text metrics.
        padding: Horizontal padding in pixels added to each column.

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

    return tuple(widths)


def calculate_rows_per_page(
    safe_area: BoundingBox,
    row_height: int = 28,
    header_height: int = 45,
) -> int:
    """Calculate the maximum number of table rows that fit within safe area height.

    Args:
        safe_area: Usable content bounding box.
        row_height: Height allocated for each data row in pixels.
        header_height: Height reserved for table header and separator in pixels.

    Returns:
        integer count of rows that fit into the available height.
    """
    usable_height = safe_area.height - header_height
    if usable_height <= 0:
        return 0
    return usable_height // row_height


def calculate_layout_boxes(
    table: TableData,
    preset: DevicePreset,
    page: int = 1,
) -> tuple[BoundingBox, ...]:
    """Calculate bounding boxes for all layout elements on the specified page.

    Args:
        table: Tabular dataset with headers and rows.
        preset: Target device layout and resolution preset.
        page: One-based page number.

    Returns:
        Tuple of BoundingBox instances representing headers, line, and cells.

    Raises:
        ValueError: If page is less than 1.
    """
    if page < 1:
        raise ValueError("Page number must be greater than or equal to 1.")

    safe_area = preset.get_safe_area()
    header_font = get_font(size=20, bold=True)
    body_font = get_font(size=18, bold=False)
    max_col_w = safe_area.width // table.column_count
    widths = calculate_column_widths(
        table=table, font=header_font, padding=40, max_column_width=max_col_w
    )

    col_x_offsets: list[int] = []
    current_x = safe_area.x
    for width in widths:
        col_x_offsets.append(current_x)
        current_x += width

    boxes: list[BoundingBox] = []
    current_y = safe_area.y

    for col_idx, header in enumerate(table.headers):
        fitted_header = truncate_to_width(
            text=header, font=header_font, max_width=max(10, widths[col_idx] - 40)
        )
        bbox = header_font.getbbox(fitted_header)
        text_w = max(1, bbox[2] - bbox[0])
        text_h = max(1, bbox[3] - bbox[1])
        boxes.append(
            BoundingBox(
                x=int(col_x_offsets[col_idx] + bbox[0]),
                y=int(current_y + bbox[1]),
                width=int(text_w),
                height=int(text_h),
            )
        )

    current_y += 30
    total_table_width = sum(widths)
    boxes.append(
        BoundingBox(
            x=safe_area.x,
            y=current_y,
            width=total_table_width,
            height=2,
        )
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
                bbox = body_font.getbbox(line)
                text_w = max(1, bbox[2] - bbox[0])
                text_h = max(1, bbox[3] - bbox[1])
                boxes.append(
                    BoundingBox(
                        x=int(col_x_offsets[col_idx] + bbox[0]),
                        y=int(current_y + line_idx * line_step + bbox[1]),
                        width=int(text_w),
                        height=int(text_h),
                    )
                )
        current_y += row_height

    return tuple(boxes)


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
        table=table, font=header_font, padding=40, max_column_width=max_col_w
    )

    col_x_offsets: list[int] = []
    current_x = safe_area.x
    for width in widths:
        col_x_offsets.append(current_x)
        current_x += width

    current_y = safe_area.y

    for col_idx, header in enumerate(table.headers):
        fitted_header = truncate_to_width(
            text=header, font=header_font, max_width=max(10, widths[col_idx] - 40)
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
