"""Tests for multi-column layout flow and device positioning."""

from __future__ import annotations

from collections.abc import Sequence

from core.boxes import calculate_layout_boxes
from core.geometry import assert_no_collisions, assert_within_safe_area
from core.layout import calculate_page_layout
from core.models import TableData
from core.presets import (
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
)


def test_phone_lockscreen_centers_compact_card() -> None:
    """Ensure PHONE_LOCKSCREEN renders a compact card centered horizontally."""
    table = TableData(
        headers=["Verb", "Translation"],
        rows=[["take", "брать, взять"], ["bring", "приносить"]],
    )
    boxes = calculate_layout_boxes(table=table, preset=PHONE_LOCKSCREEN, start_idx=0)
    safe_area = PHONE_LOCKSCREEN.get_safe_area()

    line_box = next(box for box in boxes if box.height == 2)
    assert line_box.width < safe_area.width

    expected_x = safe_area.x + (safe_area.width - line_box.width) // 2
    assert line_box.x == expected_x


def test_calculate_layout_boxes_multi_column_flow_desktop_2k() -> None:
    """Ensure DESKTOP_2K distributes 120 rows into 3 horizontal column blocks."""
    headers = ["V1", "V2", "V3", "Translation"]
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=DESKTOP_2K, start_idx=0)
    safe_area = DESKTOP_2K.get_safe_area()

    separators = [box for box in boxes if box.height == 2]
    assert len(separators) == 3

    assert separators[0].x < separators[1].x < separators[2].x

    assert_within_safe_area(boxes=boxes, safe_area=safe_area)
    assert_no_collisions(boxes)


def test_multi_column_flow_uses_fixed_compact_gutter() -> None:
    """Ensure multi-column layout maintains tight 24px gap between blocks."""
    headers = ["V1", "V2", "V3", "Translation"]
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=DESKTOP_2K, start_idx=0)
    separators = [box for box in boxes if box.height == 2]

    assert len(separators) >= 2
    actual_gap = separators[1].x - separators[0].right
    assert actual_gap == 24


def test_multi_column_group_aligns_to_right_of_safe_area() -> None:
    """Ensure column blocks align to the right edge of desktop safe area."""
    headers = ["Command", "Description"]
    rows = [[f"cmd_{i}", f"desc_{i}"] for i in range(20)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=DESKTOP_2K, start_idx=0)
    safe_area = DESKTOP_2K.get_safe_area()
    separators = [box for box in boxes if box.height == 2]

    assert separators[-1].right == safe_area.right


def test_laptop_fhd_fits_three_column_blocks() -> None:
    """Ensure LAPTOP_FHD fits 3 column blocks with adapted font sizing."""
    headers = ["Infinitive", "Past Simple", "Past Participle", "Translation"]
    sample_row = [
        "understand",
        "understood",
        "understood",
        "понимать, осознавать",
    ]
    rows = [sample_row for _ in range(120)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=LAPTOP_FHD, start_idx=0)
    separators = [box for box in boxes if box.height == 2]

    assert len(separators) == 3


def test_multi_column_balances_rows_evenly_across_blocks() -> None:
    """Ensure multi-column layouts balance row count evenly across blocks."""
    headers = ["Command", "Description"]
    rows = [[f"cmd_{i}", f"Description for command {i}"] for i in range(60)]
    table = TableData(headers=headers, rows=rows)

    layout = calculate_page_layout(table=table, preset=DESKTOP_2K, start_idx=0)

    assert layout.num_blocks == 2
    assert layout.rows_per_block == 30


def test_ipad_portrait_centers_column_blocks() -> None:
    """Ensure IPAD_PORTRAIT centers column blocks horizontally."""
    headers = ["Command", "Description"]
    rows = [[f"cmd_{i}", f"desc_{i}"] for i in range(40)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=IPAD_PORTRAIT, start_idx=0)
    safe_area = IPAD_PORTRAIT.get_safe_area()

    separators = [box for box in boxes if box.height == 2]
    total_w = separators[-1].right - separators[0].x
    expected_start = safe_area.x + (safe_area.width - total_w) // 2
    assert separators[0].x == expected_start


def test_page_layout_allocates_natural_width_for_asymmetric_columns() -> None:
    """Ensure asymmetric columns expand naturally without equal-share clamping."""
    headers = ["Category", "Lab_Test", "Normal_Range"]
    rows = [
        [
            "Lipids",
            "HDL Cholesterol",
            "Men: >40 mg/dL; women: >50 mg/dL; >=60 mg/dL is considered favorable",
        ]
    ]
    table = TableData(headers=headers, rows=rows)

    layout = calculate_page_layout(table=table, preset=LAPTOP_FHD, start_idx=0)
    safe_area = LAPTOP_FHD.get_safe_area()
    one_third_width = safe_area.width // 3

    assert layout.single_widths[2] > one_third_width
    assert layout.single_block_width <= safe_area.width


def test_page_layout_adapts_font_for_four_column_table_when_width_permits() -> None:
    """Ensure 4-column tables scale up font when vertical and horizontal space permits."""
    headers = ["Col1", "Col2", "Col3", "Col4"]
    rows = [["A", "B", "C", "D"] for _ in range(10)]
    table = TableData(headers=headers, rows=rows)

    layout = calculate_page_layout(table=table, preset=LAPTOP_FHD, start_idx=0)

    assert layout.font_size > LAPTOP_FHD.font_size


def test_page_layout_steps_down_font_to_fit_width() -> None:
    """Ensure font steps down to highest intermediate size that fits width."""
    headers = ["Category", "Test", "Range", "Long Description Header"]
    rows = [
        ["Cat", "Test Name", "10-20", "Description text that fits at intermediate size"]
        for _ in range(25)
    ]
    table = TableData(headers=headers, rows=rows)

    layout = calculate_page_layout(table=table, preset=LAPTOP_FHD, start_idx=0)

    assert layout.font_size > LAPTOP_FHD.font_size
    assert layout.single_block_width <= LAPTOP_FHD.get_safe_area().width


def test_layout_multiline_rows_do_not_overflow_safe_area() -> None:
    """Ensure multiline wrapped rows never overflow beyond safe_area bottom."""
    headers = ["Term", "Definition"]
    rows = [
        (
            f"Term {i}",
            "This is an exceptionally long definition text designed to wrap across "
            + "multiple lines in a narrow block, massively increasing dynamic row height.",
        )
        for i in range(40)
    ]
    table = TableData(headers=headers, rows=rows)
    boxes = calculate_layout_boxes(table=table, preset=PHONE_LOCKSCREEN, start_idx=0)
    safe_area = PHONE_LOCKSCREEN.get_safe_area()

    max_bottom = max(box.bottom for box in boxes)
    assert max_bottom <= safe_area.bottom, (
        f"Content overflowed vertically: bottom {max_bottom} > safe_area.bottom {safe_area.bottom}"
    )


def test_pagination_cursor_covers_every_row_exactly_once() -> None:
    """Ensure cursor pagination covers every row without gaps or duplicates."""
    headers = ["Key", "Value"]
    rows = [(f"k{i}", "wrap " * (3 + i % 5)) for i in range(150)]
    table = TableData(headers=headers, rows=rows)

    seen: list[Sequence[str]] = []
    cursor = 0
    guard = 0
    while cursor < table.row_count and guard < 100:
        layout = calculate_page_layout(table=table, preset=LAPTOP_FHD, start_idx=cursor)
        if not layout.page_rows:
            break
        seen.extend(layout.page_rows)
        cursor += len(layout.page_rows)
        guard += 1

    assert seen == list(table.rows)
