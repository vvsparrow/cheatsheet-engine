"""Tests for universal dataset validation quality gates and schema integrity."""

from __future__ import annotations

import pytest

from core.models import TableData
from core.validation import (
    DatasetSchemaError,
    DatasetValidationError,
    DuplicateEntryError,
    SortOrderError,
    assert_no_duplicates,
    assert_sorted_order,
    validate_dataset,
    validate_table_schema,
)
from data.irregular_verbs import VERBS


def test_exception_hierarchy() -> None:
    """Ensure specific validation errors inherit from base DatasetValidationError."""
    assert issubclass(DatasetSchemaError, DatasetValidationError)


@pytest.mark.parametrize(
    ("headers", "row"),
    [
        (("Lab_Test", "Normal_Range"), ("CRP", "<5 mg/L")),
        (("Category", "Lab_Test", "Normal_Range"), ("Liver", "ALT", "4-36 U/L")),
        (
            ("Category", "Lab_Test", "Range", "Pearl"),
            ("Electrolytes", "K+", "3.5-5.0", "Cardiac risk"),
        ),
        (
            ("C1", "C2", "C3", "C4", "C5", "C6", "C7"),
            ("v1", "v2", "v3", "v4", "v5", "v6", "v7"),
        ),
    ],
)
def test_validate_table_schema_accepts_arbitrary_columns(
    headers: tuple[str, ...],
    row: tuple[str, ...],
) -> None:
    """Ensure schema validation succeeds for arbitrary N columns without hardcoding."""
    table = TableData(headers=headers, rows=(row,))
    validate_table_schema(table)


def test_validate_table_schema_expected_columns_enforced() -> None:
    """Ensure DatasetSchemaError is raised when column count mismatches expected."""
    table = TableData(
        headers=("Col1", "Col2"),
        rows=(("Val1", "Val2"),),
    )
    with pytest.raises(DatasetSchemaError, match="Expected 4 columns, got 2"):
        validate_table_schema(table, expected_columns=4)


def test_validate_table_schema_rejects_empty_headers() -> None:
    """Ensure DatasetSchemaError is raised when any header is empty or whitespace."""
    table = TableData(
        headers=("Valid", "   "),
        rows=(("Val1", "Val2"),),
    )
    with pytest.raises(DatasetSchemaError, match="Header at index 1 is empty"):
        validate_table_schema(table)


def test_validate_table_schema_rejects_empty_cells() -> None:
    """Ensure DatasetSchemaError is raised on blank cell values by default."""
    table = TableData(
        headers=("Col1", "Col2"),
        rows=(("Val1", "  "),),
    )
    with pytest.raises(DatasetSchemaError, match="Empty cell detected at row 0"):
        validate_table_schema(table, allow_empty_cells=False)


def test_assert_no_duplicates_passes_on_unique_data() -> None:
    """Ensure assert_no_duplicates succeeds when all keys are distinct."""
    table = TableData(
        headers=("Lab_Test", "Normal_Range"),
        rows=(
            ("CRP", "<5 mg/L"),
            ("LDH", "125-220 U/L"),
        ),
    )
    assert_no_duplicates(table, key_index=0)


def test_assert_no_duplicates_detects_key_column_duplicate() -> None:
    """Ensure DuplicateEntryError is raised when duplicate primary key exists."""
    table = TableData(
        headers=("Lab_Test", "Normal_Range"),
        rows=(
            ("CRP", "<5 mg/L"),
            ("CRP", "different range"),
        ),
    )
    with pytest.raises(DuplicateEntryError, match="Duplicate entry 'CRP'"):
        assert_no_duplicates(table, key_index=0)


def test_assert_no_duplicates_case_insensitive_by_default() -> None:
    """Ensure duplicates are detected regardless of casing differences."""
    table = TableData(
        headers=("Command", "Description"),
        rows=(
            ("git status", "Status check"),
            ("GIT STATUS", "Uppercase duplicate"),
        ),
    )
    with pytest.raises(DuplicateEntryError, match="Duplicate entry 'GIT STATUS'"):
        assert_no_duplicates(table, key_index=0, case_sensitive=False)


def test_assert_no_duplicates_full_row_composite() -> None:
    """Ensure duplicate detection on whole row when key_index is None."""
    table = TableData(
        headers=("Category", "Subcategory"),
        rows=(
            ("Electrolytes", "Sodium"),
            ("Electrolytes", "Potassium"),
            ("Electrolytes", "Sodium"),
        ),
    )
    with pytest.raises(DuplicateEntryError, match="Duplicate row detected"):
        assert_no_duplicates(table, key_index=None)


def test_assert_sorted_order_passes_on_alphabetical_data() -> None:
    """Ensure assert_sorted_order succeeds when rows are sorted alphabetically."""
    table = TableData(
        headers=("Verb", "Past"),
        rows=(
            ("arise", "arose"),
            ("awake", "awoke"),
            ("be", "was/were"),
        ),
    )
    assert_sorted_order(table, key_index=0)


def test_assert_sorted_order_detects_out_of_order_entries() -> None:
    """Ensure SortOrderError is raised when alphabetical order is broken."""
    table = TableData(
        headers=("Verb", "Past"),
        rows=(
            ("become", "became"),
            ("begin", "began"),
            ("arise", "arose"),
        ),
    )
    with pytest.raises(SortOrderError, match="Sort order violated at row 2"):
        assert_sorted_order(table, key_index=0)


def test_validate_dataset_master_gate_integration() -> None:
    """Ensure validate_dataset orchestrates schema, uniqueness, and sort checks."""
    table = TableData(
        headers=("Test", "Range"),
        rows=(
            ("Albumin", "3.4-5.4"),
            ("Bilirubin", "0.1-1.2"),
        ),
    )
    validate_dataset(
        table=table,
        expected_columns=2,
        key_index=0,
        check_sorted=True,
    )


def test_irregular_verbs_seed_dataset_passes_quality_gate() -> None:
    """Ensure bundled irregular verbs dataset passes all strict quality gates."""
    table = TableData(
        headers=("V1 (Infinitive)", "V2 (Past)", "V3 (Participle)", "Translation"),
        rows=tuple(tuple(str(cell) for cell in row) for row in VERBS),
    )
    validate_dataset(
        table=table,
        expected_columns=4,
        key_index=0,
        check_sorted=True,
    )
