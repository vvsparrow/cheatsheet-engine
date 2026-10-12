"""Anki deck compiler for spaced repetition card generation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import genanki  # type: ignore[import-untyped]

from core.models import TableData

ANKI_CARD_CSS = """
.card {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 22px;
    text-align: center;
    color: #f0f0f0;
    background-color: #121418;
    padding: 24px;
}
hr#answer {
    border: none;
    border-top: 2px solid #64c8ff;
    margin: 18px 0;
}
.extra {
    font-size: 16px;
    color: #a0a5af;
    margin-top: 12px;
}
"""


@dataclass(frozen=True, slots=True)
class AnkiCardMapping:
    """Configuration mapping table columns to Anki card fields."""

    front_index: int = 0
    back_index: int = 1
    extra_index: int | None = None
    tag_index: int | None = None


def compile_anki_deck(
    table: TableData,
    deck_name: str,
    output_path: Path,
    mapping: AnkiCardMapping | None = None,
) -> Path:
    """Compile tabular dataset into an installable Anki deck package (.apkg).

    Args:
        table: Tabular dataset containing flashcard records.
        deck_name: Display name for the Anki deck hierarchy.
        output_path: Destination filesystem path for the .apkg file.
        mapping: Optional column index mapping for card fields.

    Returns:
        Path to the generated .apkg file.

    Raises:
        ValueError: If mapped column indices exceed table column bounds.
    """
    card_map = mapping if mapping is not None else AnkiCardMapping()
    num_cols = len(table.headers)

    for field_name, idx_val in (
        ("front_index", card_map.front_index),
        ("back_index", card_map.back_index),
        ("extra_index", card_map.extra_index),
        ("tag_index", card_map.tag_index),
    ):
        if idx_val is not None and not (0 <= idx_val < num_cols):
            raise ValueError(
                f"Index {idx_val} out of range for {num_cols} columns ({field_name})."
            )

    deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest()[:8], 16)
    model_id = int(hashlib.md5(f"{deck_name}_model".encode()).hexdigest()[:8], 16)

    model = genanki.Model(
        model_id,
        f"{deck_name} Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
            {"name": "Extra"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": (
                    '{{FrontSide}}<hr id="answer">{{Answer}}'
                    '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}'
                ),
            },
        ],
        css=ANKI_CARD_CSS,
    )

    deck: Any = genanki.Deck(deck_id, deck_name)

    for row in table.rows:
        question = row[card_map.front_index]
        answer = row[card_map.back_index]
        extra = row[card_map.extra_index] if card_map.extra_index is not None else ""

        tags: list[str] = []
        if card_map.tag_index is not None:
            tag_val = row[card_map.tag_index].strip().replace(" ", "_")
            if tag_val:
                tags.append(tag_val)

        note = genanki.Note(
            model=model,
            fields=[question, answer, extra],
            tags=tags,
        )
        deck.add_note(note)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    package = genanki.Package(deck)
    package.write_to_file(str(output_path))

    return output_path
