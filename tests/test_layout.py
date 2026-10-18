"""Tests for table layout calculations, column widths, and bounding boxes."""

from __future__ import annotations

from core.boxes import calculate_layout_boxes
from core.columns import (
    calculate_column_widths,
    calculate_rows_per_page,
)
from core.fonts import get_font
from core.geometry import assert_no_collisions
from core.layout import _compute_page_layout, calculate_page_layout
from core.models import BoundingBox, TableData
from core.presets import (
    A4_LANDSCAPE,
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
)


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
    boxes = calculate_layout_boxes(table=table, preset=LAPTOP_FHD, start_idx=0)

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
        "with deep detail and comprehensive diagnostics. "
    ) * 2

    table = TableData(
        headers=["Command", "Description"],
        rows=[
            ["git status", long_text],
            ["git commit", "Record staged snapshot changes to repository"],
        ],
    )
    boxes = calculate_layout_boxes(table=table, preset=LAPTOP_FHD, start_idx=0)

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


def test_calculate_column_widths_accounts_for_header_font() -> None:
    """Ensure column width accounts for wider bold header font metrics."""
    table = TableData(headers=["Wide Header Title"], rows=[["Short"]])
    body_font = get_font(size=18, bold=False)
    header_font = get_font(size=18, bold=True)

    regular_widths = calculate_column_widths(table=table, font=body_font)
    bold_widths = calculate_column_widths(
        table=table,
        font=body_font,
        header_font=header_font,
    )

    assert bold_widths[0] > regular_widths[0]


def test_page_layout_preserves_minimum_word_width_in_asymmetric_table() -> None:
    """Ensure columns never shrink below their longest word plus padding."""
    long_desc = " ".join(["PolicyExplanation"] * 50)
    table = TableData(
        headers=["Topic", "Rule", "Description"],
        rows=[["StatefulInspection", "DenyAllInboundTraffic", long_desc]],
    )
    layout = calculate_page_layout(table=table, preset=LAPTOP_FHD, start_idx=0)
    font = get_font(size=layout.font_size, bold=False)
    padding = 20

    bbox_col0 = font.getbbox("StatefulInspection")
    min_w0 = (bbox_col0[2] - bbox_col0[0]) + padding
    bbox_col1 = font.getbbox("DenyAllInboundTraffic")
    min_w1 = (bbox_col1[2] - bbox_col1[0]) + padding

    assert layout.single_widths[0] >= min_w0
    assert layout.single_widths[1] >= min_w1


def test_page_layout_downscales_font_to_fit_dataset_on_single_page() -> None:
    """Ensure layout downscales font to fit rows on one page when feasible."""
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(220)]
    table = TableData(headers=["V1", "V2", "V3", "Translation"], rows=rows)
    layout = calculate_page_layout(table=table, preset=DESKTOP_2K, start_idx=0)

    assert layout.page_capacity == 220
    assert layout.num_blocks >= 4
    assert layout.font_size < DESKTOP_2K.font_size


def test_compute_page_layout_scales_row_height_proportionally_when_downscaling() -> (
    None
):
    """Ensure row height compresses proportionally with font size without floor clamping."""
    headers = ["Col1", "Col2"]
    rows = [[f"A{i}", f"B{i}"] for i in range(100)]
    table = TableData(headers=headers, rows=rows)

    base_layout = _compute_page_layout(
        table=table,
        preset=A4_LANDSCAPE,
        font_size=A4_LANDSCAPE.font_size,
        start_idx=0,
    )
    scaled_layout = _compute_page_layout(
        table=table,
        preset=A4_LANDSCAPE,
        font_size=A4_LANDSCAPE.min_font_size,
        start_idx=0,
    )

    assert scaled_layout.rows_per_block > base_layout.rows_per_block


def test_page_layout_upscales_font_for_ipad_multi_column() -> None:
    """Ensure iPad scales up typography point size above baseline."""
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=["V1", "V2", "V3", "Translation"], rows=rows)
    layout = calculate_page_layout(table=table, preset=IPAD_PORTRAIT, start_idx=0)

    assert layout.font_size > IPAD_PORTRAIT.font_size
    assert layout.page_capacity == 120


def test_page_layout_preserves_base_font_for_phone_multipage() -> None:
    """Ensure multipage phone lockscreen preserves readable base font size."""
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=["V1", "V2", "V3", "Translation"], rows=rows)
    layout = calculate_page_layout(table=table, preset=PHONE_LOCKSCREEN, start_idx=0)

    assert layout.font_size == PHONE_LOCKSCREEN.font_size
    assert layout.font_size > PHONE_LOCKSCREEN.min_font_size
