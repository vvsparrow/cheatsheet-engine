"""Tests for cheatsheet layout engine and data models."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from PIL import Image
from PIL.ImageFont import FreeTypeFont

from core.engine import (
    calculate_column_widths,
    calculate_rows_per_page,
    get_font,
    render_wallpaper,
)
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


def test_get_font_regular_returns_bundled_font() -> None:
    """Ensure get_font loads the bundled regular font with the requested size."""
    font = get_font(size=24, bold=False)
    assert isinstance(font, FreeTypeFont)
    assert font.size == 24


def test_get_font_bold_returns_bundled_font() -> None:
    """Ensure get_font loads the bold font with the requested size."""
    font = get_font(size=32, bold=True)
    assert isinstance(font, FreeTypeFont)
    assert font.size == 32


def test_get_font_fallback_when_path_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure get_font falls back to Pillow default font if assets are missing."""
    import core.engine as engine_module

    monkeypatch.setattr(engine_module, "FONTS_DIR", engine_module.Path("/nonexistent"))
    font = get_font(size=20)
    assert font is not None


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
