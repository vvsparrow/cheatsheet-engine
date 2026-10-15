"""Bounding box layout generation for quality gates and collision testing."""

from __future__ import annotations

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.fonts import get_font
from core.layout import calculate_page_layout
from core.models import BoundingBox, TableData
from core.presets import (
    A4_LANDSCAPE,
    A4_PORTRAIT,
    IPAD_PORTRAIT,
    PHONE_LOCKSCREEN,
    DevicePreset,
)
from core.typography import truncate_to_width, wrap_text


def _make_text_box(
    x: int,
    y: int,
    text: str,
    font: FreeTypeFont | ImageFont.ImageFont,
) -> BoundingBox:
    """Construct an Axis-Aligned BoundingBox for rendered text line."""
    bbox = font.getbbox(text)
    return BoundingBox(
        x=int(x + bbox[0]),
        y=int(y + bbox[1]),
        width=max(1, int(bbox[2] - bbox[0])),
        height=max(1, int(bbox[3] - bbox[1])),
    )


def calculate_layout_boxes(
    table: TableData,
    preset: DevicePreset,
    start_idx: int = 0,
) -> tuple[BoundingBox, ...]:
    """Calculate bounding boxes for all layout elements from a start index.

    Args:
        table: Tabular dataset with headers and rows.
        preset: Target device layout and resolution preset.
        start_idx: Zero-based index of the first data row to render.

    Returns:
        Tuple of BoundingBox instances representing headers, line, and cells.

    Raises:
        ValueError: If start_idx is negative.
    """
    if start_idx < 0:
        raise ValueError("start_idx must be greater than or equal to 0.")

    layout = calculate_page_layout(table=table, preset=preset, start_idx=start_idx)
    if layout.rows_per_block <= 0:
        return ()

    safe_area = preset.get_safe_area()
    header_font = get_font(size=layout.font_size, bold=True)
    body_font = get_font(size=layout.font_size, bold=False)
    boxes: list[BoundingBox] = []

    total_content_w = (
        layout.num_blocks * layout.single_block_width
        + (layout.num_blocks - 1) * layout.gutter
    )

    if preset in (IPAD_PORTRAIT, PHONE_LOCKSCREEN, A4_PORTRAIT, A4_LANDSCAPE):
        start_x = safe_area.x + (safe_area.width - total_content_w) // 2
    else:
        start_x = safe_area.right - total_content_w

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
            boxes.append(
                _make_text_box(
                    x=col_x_offsets[col_idx] + 10,
                    y=current_y,
                    text=fitted_header,
                    font=header_font,
                )
            )

        current_y += max(36, int(layout.font_size * 1.45))
        boxes.append(
            BoundingBox(
                x=block_x,
                y=current_y,
                width=layout.single_block_width,
                height=2,
            )
        )
        current_y += max(15, int(layout.font_size * 0.5))

        b_start = block_idx * layout.rows_per_block
        b_end = b_start + layout.rows_per_block
        block_rows = layout.page_rows[b_start:b_end]

        for row in block_rows:
            row_lines = [
                wrap_text(
                    text=cell,
                    font=body_font,
                    max_width=max(10, layout.single_widths[col_idx] - 20),
                )
                for col_idx, cell in enumerate(row)
            ]
            num_lines = max((len(lines) for lines in row_lines), default=1)
            line_step = int(layout.font_size * 1.45)
            pad_y = max(4, int(layout.font_size * 0.2))
            row_height = num_lines * line_step + 2 * pad_y

            for col_idx, lines in enumerate(row_lines):
                for line_idx, line in enumerate(lines):
                    if not line:
                        continue
                    boxes.append(
                        _make_text_box(
                            x=col_x_offsets[col_idx] + 10,
                            y=current_y + pad_y + line_idx * line_step,
                            text=line,
                            font=body_font,
                        )
                    )
            current_y += row_height

    return tuple(boxes)
