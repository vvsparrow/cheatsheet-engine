"""Tests for Anki deck compilation and spaced repetition card export."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from core.anki import AnkiCardMapping, compile_anki_deck
from core.models import TableData


def test_anki_card_mapping_defaults_and_immutability() -> None:
    """Ensure AnkiCardMapping instantiates with defaults and is immutable."""
    mapping = AnkiCardMapping()
    assert mapping.front_index == 0
    assert mapping.back_index == 1
    assert mapping.extra_index is None
    assert mapping.tag_index is None

    with pytest.raises(AttributeError):
        mapping.front_index = 2  # type: ignore[misc]


def test_compile_anki_deck_generates_valid_apkg(tmp_path: Path) -> None:
    """Ensure compile_anki_deck creates valid .apkg containing Anki SQLite collection."""
    table = TableData(
        headers=("Lab_Test", "Normal_Range", "Clinical_Pearl", "Category"),
        rows=(
            ("Potassium (K+)", "3.5-5.0 mEq/L", "Risk of dysrhythmias", "Electrolytes"),
            ("Sodium (Na+)", "135-145 mEq/L", "Risk of seizures", "Electrolytes"),
        ),
    )
    mapping = AnkiCardMapping(
        front_index=0,
        back_index=1,
        extra_index=2,
        tag_index=3,
    )
    output_apkg = tmp_path / "nclex_electrolytes.apkg"

    result_path = compile_anki_deck(
        table=table,
        deck_name="NCLEX::Electrolytes",
        mapping=mapping,
        output_path=output_apkg,
    )

    assert result_path == output_apkg
    assert result_path.is_file()
    assert result_path.stat().st_size > 0

    with zipfile.ZipFile(result_path, "r") as archive:
        namelist = archive.namelist()
        assert "collection.anki2" in namelist


def test_compile_anki_deck_invalid_mapping_raises(tmp_path: Path) -> None:
    """Ensure ValueError is raised when mapping indices exceed table columns."""
    table = TableData(
        headers=("Col1", "Col2"),
        rows=(("Val1", "Val2"),),
    )
    mapping = AnkiCardMapping(front_index=0, back_index=5)
    out_file = tmp_path / "invalid.apkg"

    with pytest.raises(ValueError, match="Index 5 out of range for 2 columns"):
        compile_anki_deck(
            table=table,
            deck_name="Test Deck",
            mapping=mapping,
            output_path=out_file,
        )
