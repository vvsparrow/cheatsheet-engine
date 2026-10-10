"""Integration tests for cheatsheet wallpaper rendering engine."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from PIL import Image

from core.engine import render_card_pack, render_wallpaper
from core.models import TableData
from core.presets import DESKTOP_2K, LAPTOP_FHD, PHONE_LOCKSCREEN


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
        ["git commit"],
    ]
    with pytest.raises(ValueError, match="Row length mismatch"):
        TableData(headers=headers, rows=rows)


def test_table_data_is_immutable() -> None:
    """Ensure TableData enforces immutability via FrozenInstanceError."""
    table = TableData(headers=["A", "B"], rows=[["1", "2"]])
    with pytest.raises(FrozenInstanceError):
        table.headers = ("C", "D")  # type: ignore[misc]


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
        assert img.size == (
            LAPTOP_FHD.resolution.width,
            LAPTOP_FHD.resolution.height,
        )


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


def test_render_wallpaper_pagination_renders_distinct_pages(
    tmp_path: Path,
) -> None:
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


def test_render_wallpaper_invalid_page_raises_value_error(
    tmp_path: Path,
) -> None:
    """Ensure render_wallpaper raises ValueError when page is less than 1."""
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


def test_render_wallpaper_multi_column_desktop_2k(tmp_path: Path) -> None:
    """Ensure render_wallpaper draws multi-column blocks across 2K display."""
    headers = ["V1", "V2", "V3", "Translation"]
    rows = [[f"v1_{i}", f"v2_{i}", f"v3_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=headers, rows=rows)
    output_path = tmp_path / "desktop_2k_wallpaper.png"

    result = render_wallpaper(
        table=table,
        preset=DESKTOP_2K,
        output_path=output_path,
        page=1,
    )

    assert result.is_file()
    with Image.open(result) as img:
        assert img.size == (2560, 1440)
        # Проверяем, что в правой трети экрана (x > 1700) есть отрисованный текст,
        # а не сплошной фоновый цвет (18, 20, 24)
        right_crop = img.crop((1700, 100, 2400, 600))
        colors = right_crop.getcolors(maxcolors=2400 * 600)
        assert colors is not None
        assert len(colors) > 1  # Больше 1 цвета означает наличие текста


def test_render_card_pack_generates_all_pages(tmp_path: Path) -> None:
    """Ensure render_card_pack renders complete numbered series of cards."""
    headers = ["Verb", "Translation"]
    rows = [[f"verb_{i}", f"trans_{i}"] for i in range(120)]
    table = TableData(headers=headers, rows=rows)
    cards_dir = tmp_path / "mobile_cards"

    generated_paths = render_card_pack(
        table=table,
        preset=PHONE_LOCKSCREEN,
        output_dir=cards_dir,
    )

    assert len(generated_paths) > 1
    assert cards_dir.is_dir()

    total_cards = len(generated_paths)
    for idx, card_path in enumerate(generated_paths, start=1):
        assert card_path.is_file()
        assert f"part_{idx}_of_{total_cards}.png" in card_path.name
        with Image.open(card_path) as img:
            assert img.size == (
                PHONE_LOCKSCREEN.resolution.width,
                PHONE_LOCKSCREEN.resolution.height,
            )
