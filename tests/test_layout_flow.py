"""Tests for multi-column layout flow and device positioning."""

from __future__ import annotations

from core.boxes import calculate_layout_boxes
from core.geometry import assert_no_collisions, assert_within_safe_area
from core.layout import calculate_page_layout
from core.models import TableData
from core.presets import (
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
)


def test_phone_lockscreen_centers_compact_card() -> None:
    """Ensure PHONE_LOCKSCREEN renders a compact card centered horizontally."""
    table = TableData(
        headers=["Verb", "Translation"],
        rows=[["take", "брать, взять"], ["bring", "приносить"]],
    )
    boxes = calculate_layout_boxes(table=table, preset=PHONE_LOCKSCREEN, page=1)
    safe_area = PHONE_LOCKSCREEN.get_safe_area()

    line_box = next(box for box in boxes if box.height == 2)
    # Карточка компактна (не раздута искусственно на всю ширину)
    assert line_box.width < safe_area.width

    # Карточка идеально отцентрирована внутри safe_area
    expected_x = safe_area.x + (safe_area.width - line_box.width) // 2
    assert line_box.x == expected_x


def test_calculate_layout_boxes_multi_column_flow_desktop_2k() -> None:
    """Ensure DESKTOP_2K distributes 120 rows into 3 horizontal column blocks."""
    headers = ["V1", "V2", "V3", "Translation"]
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=DESKTOP_2K, page=1)
    safe_area = DESKTOP_2K.get_safe_area()

    separators = [box for box in boxes if box.height == 2]
    assert len(separators) == 3

    assert separators[0].x < separators[1].x < separators[2].x

    assert_within_safe_area(boxes=boxes, safe_area=safe_area)
    assert_no_collisions(boxes)


def test_phone_panorama_partitions_across_three_swipe_panels() -> None:
    """Ensure PHONE_PANORAMA aligns 3 column blocks with 1080px swipe screens."""
    headers = ["V1", "V2", "V3", "Translation"]
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=PHONE_PANORAMA, page=1)

    separators = [box for box in boxes if box.height == 2]
    assert len(separators) == 3

    panel_w = PHONE_PANORAMA.resolution.width // 3
    expected_offset = (panel_w - separators[0].width) // 2
    assert separators[0].x == expected_offset
    assert separators[1].x == panel_w + expected_offset
    assert separators[2].x == 2 * panel_w + expected_offset


def test_multi_column_flow_uses_fixed_compact_gutter() -> None:
    """Ensure multi-column layout maintains tight 24px gap between blocks."""
    headers = ["V1", "V2", "V3", "Translation"]
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=DESKTOP_2K, page=1)
    separators = [box for box in boxes if box.height == 2]

    assert len(separators) >= 2
    actual_gap = separators[1].x - separators[0].right
    assert actual_gap == 24


def test_multi_column_group_aligns_to_right_of_safe_area() -> None:
    """Ensure column blocks align to the right edge of desktop safe area."""
    headers = ["Command", "Description"]
    rows = [[f"cmd_{i}", f"desc_{i}"] for i in range(20)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=DESKTOP_2K, page=1)
    safe_area = DESKTOP_2K.get_safe_area()
    separators = [box for box in boxes if box.height == 2]

    # Последний разделитель должен заканчиваться ровно у правого края safe_area
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

    boxes = calculate_layout_boxes(table=table, preset=LAPTOP_FHD, page=1)
    separators = [box for box in boxes if box.height == 2]

    assert len(separators) == 3


def test_multi_column_balances_rows_evenly_across_blocks() -> None:
    """Ensure multi-column layouts balance row count evenly across blocks."""
    headers = ["Command", "Description"]
    rows = [[f"cmd_{i}", f"Description for command {i}"] for i in range(60)]
    table = TableData(headers=headers, rows=rows)

    layout = calculate_page_layout(table=table, preset=DESKTOP_2K, page=1)

    # 60 строк требуют 2 блока (при макс. высоте 43).
    # Без балансировки было бы 43 строки в первом блоке и 17 во втором.
    # С балансировкой: ceil(60 / 2) = 30 строк в каждом блоке.
    assert layout.num_blocks == 2
    assert layout.rows_per_block == 30


def test_ipad_portrait_centers_column_blocks() -> None:
    """Ensure IPAD_PORTRAIT centers column blocks horizontally."""
    headers = ["Command", "Description"]
    rows = [[f"cmd_{i}", f"desc_{i}"] for i in range(40)]
    table = TableData(headers=headers, rows=rows)

    boxes = calculate_layout_boxes(table=table, preset=IPAD_PORTRAIT, page=1)
    safe_area = IPAD_PORTRAIT.get_safe_area()

    separators = [box for box in boxes if box.height == 2]
    total_w = separators[-1].right - separators[0].x
    expected_start = safe_area.x + (safe_area.width - total_w) // 2
    assert separators[0].x == expected_start
