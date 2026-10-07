"""Tests for cheatsheet layout engine and data models."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from PIL.ImageFont import FreeTypeFont

from core.engine import calculate_column_widths, get_font
from core.models import TableData


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
