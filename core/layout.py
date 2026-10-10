"""Layout calculations and element bounding box generation."""

from __future__ import annotations

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from core.fonts import get_font
from core.models import BoundingBox, TableData
from core.presets import PHONE_LOCKSCREEN, DevicePreset
from core.typography import truncate_to_width, wrap_text


def calculate_column_widths(
    table: TableData,
    font: FreeTypeFont | ImageFont.ImageFont,
    padding: int = 20,
    max_column_width: int | None = None,
    target_width: int | None = None,
) -> tuple[int, ...]:
    """Calculate dynamic column widths based on maximum text bounding boxes.

    Args:
        table: Tabular dataset with headers and rows.
        font: Font used to measure rendered text metrics.
        padding: Horizontal padding in pixels added to each column.
        max_column_width: Optional upper bound constraint for column width.
        target_width: Optional width in pixels to stretch columns to.

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

    if target_width is not None and target_width > 0 and widths:
        total_w = sum(widths)
        if 0 < total_w < target_width:
            scale = target_width / total_w
            scaled_widths = [int(w * scale) for w in widths]
            remainder = target_width - sum(scaled_widths)
            scaled_widths[-1] += remainder
            widths = scaled_widths
        elif total_w == 0:
            base_w = target_width // len(widths)
            scaled_widths = [base_w] * len(widths)
            remainder = target_width - sum(scaled_widths)
            scaled_widths[-1] += remainder
            widths = scaled_widths

    return tuple(widths)


def calculate_rows_per_page(
    safe_area: BoundingBox,
    row_height: int = 28,
    header_height: int = 45,
) -> int:
    """Calculate maximum table rows that fit within safe area height.

    Args:
        safe_area: Usable content bounding box.
        row_height: Height allocated for each data row in pixels.
        header_height: Height reserved for table header and separator.

    Returns:
        Integer count of rows that fit into the available height.
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
        return ()

    min_gutter = 40
    if preset == PHONE_LOCKSCREEN or single_block_width >= safe_area.width:
        max_blocks = 1
    else:
        max_blocks = max(
            1,
            (safe_area.width + min_gutter) // max(1, single_block_width + min_gutter),
        )

    # Определяем диапазон строк для текущей страницы
    page_capacity = rows_per_block * max_blocks
    start_row_idx = (page - 1) * page_capacity
    end_row_idx = start_row_idx + page_capacity
    page_rows = table.rows[start_row_idx:end_row_idx]

    if not page_rows:
        num_blocks = 1
    else:
        needed_blocks = (len(page_rows) + rows_per_block - 1) // rows_per_block
        num_blocks = max(1, min(max_blocks, needed_blocks))

    if num_blocks > 1:
        total_content_w = num_blocks * single_block_width
        gutter = (safe_area.width - total_content_w) // (num_blocks - 1)
    else:
        gutter = 0

    boxes: list[BoundingBox] = []

    for block_idx in range(num_blocks):
        block_x = safe_area.x + block_idx * (single_block_width + gutter)
        current_y = safe_area.y

        col_x_offsets: list[int] = []
        curr_x = block_x
        for w in single_widths:
            col_x_offsets.append(curr_x)
            curr_x += w

        # Шапка текущего блока
        for col_idx, header in enumerate(table.headers):
            fitted_header = truncate_to_width(
                text=header,
                font=header_font,
                max_width=max(10, single_widths[col_idx] - 40),
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
        boxes.append(
            BoundingBox(
                x=block_x,
                y=current_y,
                width=single_block_width,
                height=2,
            )
        )
        current_y += 15

        # Строки данных текущего блока
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
