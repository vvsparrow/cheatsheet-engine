"""Tests for table layout calculations, column widths, and bounding boxes."""

from __future__ import annotations

from core.fonts import get_font
from core.geometry import assert_no_collisions
from core.layout import (
    calculate_column_widths,
    calculate_layout_boxes,
    calculate_rows_per_page,
)
from core.models import BoundingBox, TableData
from core.presets import LAPTOP_FHD, PHONE_LOCKSCREEN


def test_calculate_column_widths_respects_content_and_padding() -> None:
    """Ensure calculate_column_widths accounts for longest cell and padding."""
    table = TableData(
        headers=["ID", "Long Header Description"],
        rows=[["1", "Short"], ["99999", "Tiny"]],
    )
    font = get_font(size=20)
    padding = 30
    widths = calculate_column_widths(table=table, font=font, padding=padding)

    assert len(widths) == 2
    assert widths[1] > widths[0]

    bbox_id = font.getbbox("99999")
    text_width_0 = bbox_id[2] - bbox_id[0]
    assert widths[0] >= text_width_0 + padding


def test_calculate_rows_per_page_fits_within_safe_area() -> None:
    """Ensure calculate_rows_per_page computes exact rows fitting height."""
    safe_area = BoundingBox(x=0, y=0, width=1920, height=325)
    rows_per_page = calculate_rows_per_page(
        safe_area=safe_area,
        row_height=28,
        header_height=45,
    )
    assert rows_per_page == 10


def test_calculate_layout_boxes_counts_and_boundaries() -> None:
    """Ensure calculate_layout_boxes returns bboxes for table elements."""
    table = TableData(
        headers=["Col A", "Col B"],
        rows=[["Val 1", "Val 2"], ["Val 3", "Val 4"]],
    )
    boxes = calculate_layout_boxes(table=table, preset=LAPTOP_FHD, page=1)

    assert len(boxes) == 7
    for box in boxes:
        assert isinstance(box, BoundingBox)
        assert box.width > 0
        assert box.height > 0


def test_calculate_column_widths_with_empty_rows() -> None:
    """Ensure calculate_column_widths works when table has no data rows."""
    table = TableData(headers=["Header One", "Header Two"], rows=[])
    font = get_font(size=20)
    widths = calculate_column_widths(table=table, font=font, padding=20)

    assert len(widths) == 2
    bbox = font.getbbox("Header One")
    assert widths[0] >= (bbox[2] - bbox[0] + 20)


def test_calculate_column_widths_caps_at_max_column_width() -> None:
    """Ensure calculate_column_widths clamps columns exceeding max width."""
    font = get_font(size=18, bold=False)
    table = TableData(
        headers=["LongHeaderTitleThatExceedsLimit"],
        rows=[["ExtremelyLongDataRowContentThatShouldBeCapped"]],
    )
    widths = calculate_column_widths(
        table=table, font=font, padding=20, max_column_width=150
    )
    assert widths == (150,)


def test_calculate_layout_boxes_wrapped_rows_no_collisions() -> None:
    """Ensure wrapped lines dynamically adjust row heights without collisions."""
    long_text = (
        "Show working tree status and list untracked or modified files "
        "across all working directories, repositories, and local branches "
        "with deep detail and comprehensive diagnostics"
    )
    table = TableData(
        headers=["Command", "Description"],
        rows=[
            ["git status", long_text],
            ["git commit", "Record staged snapshot changes to repository"],
        ],
    )
    boxes = calculate_layout_boxes(table=table, preset=LAPTOP_FHD, page=1)

    assert len(boxes) > 7
    assert_no_collisions(boxes)


def test_calculate_column_widths_justifies_to_target_width() -> None:
    """Ensure calculate_column_widths stretches columns to match target."""
    table = TableData(
        headers=["Verb", "Translation"],
        rows=[["take", "брать, взять"], ["bring", "приносить"]],
    )
    font = get_font(size=20)
    target_width = 1290

    widths = calculate_column_widths(
        table=table,
        font=font,
        padding=20,
        target_width=target_width,
    )

    assert len(widths) == 2
    assert sum(widths) == target_width
    assert widths[1] > widths[0]


def test_calculate_column_widths_no_shrink_when_content_wider() -> None:
    """Ensure calculate_column_widths does not shrink below natural width."""
    table = TableData(
        headers=["Verb", "Translation"],
        rows=[["take", "брать, взять"], ["bring", "приносить"]],
    )
    font = get_font(size=20)
    natural_widths = calculate_column_widths(table=table, font=font, padding=20)
    natural_total = sum(natural_widths)

    widths = calculate_column_widths(
        table=table,
        font=font,
        padding=20,
        target_width=natural_total - 100,
    )

    assert widths == natural_widths


def test_phone_lockscreen_stretches_to_safe_area_width() -> None:
    """Ensure PHONE_LOCKSCREEN expands table width to fill safe area."""
    table = TableData(
        headers=["Verb", "Translation"],
        rows=[["take", "брать, взять"], ["bring", "приносить"]],
    )
    boxes = calculate_layout_boxes(table=table, preset=PHONE_LOCKSCREEN, page=1)
    safe_area = PHONE_LOCKSCREEN.get_safe_area()

    # Сепаратор (высота 2px) должен растянуться на всю ширину safe_area
    line_box = next(box for box in boxes if box.height == 2)
    assert line_box.width == safe_area.width
