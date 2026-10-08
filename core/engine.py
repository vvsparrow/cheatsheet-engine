"""Layout and rendering engine for cheatsheet wallpapers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from core.models import BoundingBox, TableData
from core.presets import DevicePreset

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def get_font(size: int, bold: bool = False) -> FreeTypeFont | ImageFont.ImageFont:
    """Load a bundled font by size and weight with fallback to default font.

    Args:
        size: Font point size.
        bold: Whether to load bold typeface weight.

    Returns:
        Loaded FreeTypeFont or Pillow fallback font.
    """
    font_name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    font_path = FONTS_DIR / font_name

    try:
        return ImageFont.truetype(str(font_path), size=size)
    except OSError:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def calculate_column_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    padding: int = 20,
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

        widths.append(int(max_width + padding))

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
    widths = calculate_column_widths(table=table, font=header_font, padding=40)

    col_x_offsets: list[int] = []
    current_x = safe_area.x
    for width in widths:
        col_x_offsets.append(current_x)
        current_x += width

    current_y = safe_area.y

    for col_idx, header in enumerate(table.headers):
        draw.text(
            (col_x_offsets[col_idx], current_y),
            header,
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

    row_height = 28
    rows_per_page = calculate_rows_per_page(
        safe_area=safe_area,
        row_height=row_height,
        header_height=45,
    )
    if rows_per_page > 0:
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        visible_rows = table.rows[start_idx:end_idx]
    else:
        visible_rows = ()

    for row in visible_rows:
        for col_idx, cell in enumerate(row):
            draw.text(
                (col_x_offsets[col_idx], current_y),
                cell,
                fill=(240, 240, 240),
                font=body_font,
            )
        current_y += row_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path
