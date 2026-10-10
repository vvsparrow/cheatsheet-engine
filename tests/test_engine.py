"""Tests for cheatsheet layout engine and data models."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from PIL import Image

from core.engine import (
    calculate_column_widths,
    calculate_layout_boxes,
    calculate_rows_per_page,
    render_wallpaper,
)
from core.fonts import get_font
from core.geometry import assert_no_collisions
from core.models import BoundingBox, TableData
from core.presets import LAPTOP_FHD


def test_table_data_valid_instantiation() -> None:
    """Ensure TableData instantiates correctly with matching row lengths."""
    headers = ["Command", "Description"]
    rows = [
        ["git status", "Show working tree status"],
        ["git commit", "Record changes to repository"],
    ]
    table = TableData(headers=headers, rows=rows)

    assert table.headers == ("Command", "Description")
    assert table.rows == (
        ("git status", "Show working tree status"),
        ("git commit", "Record changes to repository"),
    )
    assert table.column_count == 2
    assert table.row_count == 2


def test_table_data_empty_headers_raises_value_error() -> None:
    """Ensure TableData raises ValueError when headers are empty."""
    with pytest.raises(ValueError, match="Headers cannot be empty"):
        TableData(headers=[], rows=[])


def test_table_data_row_length_mismatch_raises_value_error() -> None:
    """Ensure TableData raises ValueError when row lengths does not match headers."""
    headers = ["Command", "Description"]
    rows = [
        ["git status", "Show status"],
        ["git commit"],  # 1 element instead of 2
    ]
    with pytest.raises(ValueError, match="Row length mismatch"):
        TableData(headers=headers, rows=rows)


def test_table_data_is_immutable() -> None:
    """Ensure  TableData enforces immutability via FrozenInstanceError."""
    table = TableData(headers=["A", "B"], rows=[["1", "2"]])
    with pytest.raises(FrozenInstanceError):
        table.headers = ("C", "D")  # type: ignore[misc]


def test_calculate_column_widths_respects_content_and_padding() -> None:
    """Ensure calculate_column_widths accounts for longest cell and column padding."""
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


def test_calculate_column_widths_with_empty_rows() -> None:
    """Ensure calculate_column_widths works when table has no data rows."""
    table = TableData(headers=["Header One", "Header Two"], rows=[])
    font = get_font(size=20)
    widths = calculate_column_widths(table=table, font=font, padding=20)

    assert len(widths) == 2
    bbox = font.getbbox("Header One")
    assert widths[0] >= (bbox[2] - bbox[0] + 20)


def test_render_wallpaper_creates_image_file(tmp_path: Path) -> None:
    """Ensure render_wallpaper creates an image matching the preset resolution."""
    output_path = tmp_path / "test_wallpaper.png"
    table = TableData(
        headers=["Command", "Description"],
        rows=[["git status", "Show working tree status"]],
    )

    result_path = render_wallpaper(
        table=table,
        preset=LAPTOP_FHD,
        output_path=output_path,
    )

    assert result_path == output_path
    assert result_path.is_file()
    with Image.open(result_path) as img:
        assert img.size == (LAPTOP_FHD.resolution.width, LAPTOP_FHD.resolution.height)


def test_render_wallpaper_draws_content(tmp_path: Path) -> None:
    """Ensure render_wallpaper renders headers, rows, and graphic elements."""
    output_path = tmp_path / "content_wallpaper.png"
    table = TableData(
        headers=["Col1", "Col2"],
        rows=[["Val1", "Val2"]],
    )

    render_wallpaper(
        table=table,
        preset=LAPTOP_FHD,
        output_path=output_path,
    )

    with Image.open(output_path) as img:
        total_pixels = LAPTOP_FHD.resolution.width * LAPTOP_FHD.resolution.height
        colors = img.getcolors(maxcolors=total_pixels)
        assert colors is not None
        assert len(colors) > 1


def test_calculate_rows_per_page_fits_within_safe_area() -> None:
    """Ensure calculate_rows_per_page computes exact rows fitting safe area height."""
    safe_area = BoundingBox(x=0, y=0, width=1920, height=325)
    rows_per_page = calculate_rows_per_page(
        safe_area=safe_area,
        row_height=28,
        header_height=45,
    )
    assert rows_per_page == 10


def test_render_wallpaper_pagination_renders_distinct_pages(tmp_path: Path) -> None:
    """Ensure render_wallpaper renders distinct content for different pages."""
    table = TableData(
        headers=["Command", "Description"],
        rows=[[f"cmd_{i}", f"desc_{i}"] for i in range(50)],
    )
    page_1_path = tmp_path / "page_1.png"
    page_2_path = tmp_path / "page_2.png"

    render_wallpaper(table=table, preset=LAPTOP_FHD, output_path=page_1_path, page=1)
    render_wallpaper(table=table, preset=LAPTOP_FHD, output_path=page_2_path, page=2)

    assert page_1_path.read_bytes() != page_2_path.read_bytes()


def test_render_wallpaper_invalid_page_raises_value_error(tmp_path: Path) -> None:
    """Ensure render_wallpaper raises ValueError when page number is less than 1."""
    table = TableData(headers=["Command"], rows=[["ls"]])
    with pytest.raises(
        ValueError, match="Page number must be greater than or equal to 1"
    ):
        render_wallpaper(
            table=table,
            preset=LAPTOP_FHD,
            output_path=tmp_path / "test.png",
            page=0,
        )


def test_calculate_layout_boxes_counts_and_boundaries() -> None:
    """Ensure calculate_layout_boxes returns bboxes for headers, line, and
    cell."""
    table = TableData(
        headers=["Col A", "Col B"], rows=[["Val 1", "Val 2"], ["Val 3", "Val 4"]]
    )
    boxes = calculate_layout_boxes(table=table, preset=LAPTOP_FHD, page=1)

    assert len(boxes) == 7
    for box in boxes:
        assert isinstance(box, BoundingBox)
        assert box.width > 0
        assert box.height > 0


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

    # 2 headers + 1 separator line + 1 git status cell + >1 wrapped lines + 2 for row 2
    assert len(boxes) > 7
    assert_no_collisions(boxes)


def test_render_wallpaper_defensive_layout(tmp_path: Path) -> None:
    """Ensure render_wallpaper renders overflowing and multi-word text safely."""
    overflow_word = "SupercalifragilisticexpialidociousLongUnbrokenTokenString"
    long_phrase = "Detailed explanation of system status across environments " * 5
    table = TableData(
        headers=["Component", "Details"],
        rows=[
            ["Telemetry", long_phrase],
            [overflow_word, "Normal description"],
        ],
    )
    output_path = tmp_path / "defensive_layout.png"
    result = render_wallpaper(table=table, preset=LAPTOP_FHD, output_path=output_path)

    assert result.is_file()
    assert result.stat().st_size > 0
