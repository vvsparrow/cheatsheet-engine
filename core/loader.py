"""Dataset loading utilities for tabular file ingestion."""

from __future__ import annotations

import csv
from pathlib import Path

from core.models import TableData
from data.irregular_verbs import VERBS

__all__ = ["build_default_table", "load_dataset_from_csv"]


def load_dataset_from_csv(csv_path: Path) -> TableData:
    """Load and parse tabular dataset from a CSV file.

    Args:
        csv_path: Path to the source CSV file.

    Returns:
        TableData model instance containing parsed headers and rows.

    Raises:
        ValueError: If CSV file is empty.
    """
    with csv_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        records = [tuple(cell.strip() for cell in row) for row in reader if row]

    if not records:
        raise ValueError(f"CSV file is empty: {csv_path}")

    return TableData(headers=records[0], rows=tuple(records[1:]))


def build_default_table() -> TableData:
    """Build fallback default TableData from irregular verbs seed data.

    Returns:
        TableData containing standard irregular verbs table.
    """
    return TableData(
        headers=(
            "V1 (Infinitive)",
            "V2 (Past)",
            "V3 (Participle)",
            "Translation",
        ),
        rows=tuple(tuple(str(cell) for cell in row) for row in VERBS),
    )
