"""Dataset quality gates, schema integrity checks, and validation rules."""

from __future__ import annotations

from core.models import TableData


class DatasetValidationError(Exception):
    """Base domain exception for dataset quality gate violations."""


class DatasetSchemaError(DatasetValidationError):
    """Raised when tabular data violates schema structure or column constraints."""


class DuplicateEntryError(DatasetValidationError):
    """Raised when duplicate rows or keys are detected in a dataset."""


class SortOrderError(DatasetValidationError):
    """Raised when dataset rows violate expected lexicographical sort order."""


def validate_table_schema(
    table: TableData,
    expected_columns: int | None = None,
    allow_empty_cells: bool = False,
) -> None:
    """Validate table structural schema and cell invariants for arbitrary dimensions.

    Args:
        table: Tabular dataset to validate.
        expected_columns: Optional exact column count constraint.
        allow_empty_cells: Whether empty or whitespace cells are permitted.

    Raises:
        DatasetSchemaError: If any header or cell violates schema invariants.
    """
    for idx, header in enumerate(table.headers):
        if not header.strip():
            raise DatasetSchemaError(f"Header at index {idx} is empty or whitespace.")

    if expected_columns is not None and len(table.headers) != expected_columns:
        raise DatasetSchemaError(
            f"Expected {expected_columns} columns, got {len(table.headers)}."
        )

    if not allow_empty_cells:
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row):
                if not cell.strip():
                    raise DatasetSchemaError(
                        f"Empty cell detected at row {row_idx}, column {col_idx}."
                    )


def assert_no_duplicates(
    table: TableData,
    key_index: int | None = 0,
    case_sensitive: bool = False,
) -> None:
    """Ensure dataset contains no duplicate rows or key column values.

    Args:
        table: Tabular dataset to inspect.
        key_index: Column index to treat as unique key, or None for whole row.
        case_sensitive: Whether string comparisons should differentiate case.

    Raises:
        ValueError: If key_index is outside valid column range.
        DuplicateEntryError: If a duplicate key or row is detected.
    """
    if key_index is not None and not (0 <= key_index < len(table.headers)):
        raise ValueError(
            f"Key index {key_index} out of range for {len(table.headers)} columns."
        )

    seen: dict[object, int] = {}

    for row_idx, row in enumerate(table.rows):
        if key_index is None:
            key: object = (
                row if case_sensitive else tuple(cell.strip().lower() for cell in row)
            )
            raw_repr = str(row)
        else:
            raw_val = row[key_index]
            key = raw_val.strip() if case_sensitive else raw_val.strip().lower()
            raw_repr = raw_val

        if key in seen:
            prev_row = seen[key]
            if key_index is None:
                raise DuplicateEntryError(
                    f"Duplicate row detected at index {row_idx} "
                    f"(identical to row {prev_row}): {raw_repr}"
                )
            raise DuplicateEntryError(
                f"Duplicate entry '{raw_repr}' at row {row_idx} "
                f"(previously seen at row {prev_row})."
            )

        seen[key] = row_idx


def assert_sorted_order(
    table: TableData,
    key_index: int = 0,
    case_sensitive: bool = False,
    reverse: bool = False,
) -> None:
    """Ensure table rows are sorted strictly in designated key column order.

    Args:
        table: Tabular dataset to inspect.
        key_index: Column index to evaluate sort order against.
        case_sensitive: Whether string comparisons should differentiate case.
        reverse: True if descending order is expected, False for ascending.

    Raises:
        ValueError: If key_index is outside valid column range.
        SortOrderError: If any row is out of sorted order.
    """
    if not (0 <= key_index < len(table.headers)):
        raise ValueError(
            f"Key index {key_index} out of range for {len(table.headers)} columns."
        )

    if len(table.rows) <= 1:
        return

    for i in range(1, len(table.rows)):
        prev_raw = table.rows[i - 1][key_index]
        curr_raw = table.rows[i][key_index]

        prev_val = prev_raw.strip() if case_sensitive else prev_raw.strip().lower()
        curr_val = curr_raw.strip() if case_sensitive else curr_raw.strip().lower()

        if reverse:
            if curr_val > prev_val:
                raise SortOrderError(
                    f"Sort order violated at row {i}: '{curr_raw}' "
                    f"should not follow '{prev_raw}' in descending order."
                )
        else:
            if curr_val < prev_val:
                raise SortOrderError(
                    f"Sort order violated at row {i}: '{curr_raw}' "
                    f"should not follow '{prev_raw}' in ascending order."
                )


def validate_dataset(
    table: TableData,
    expected_columns: int | None = None,
    key_index: int | None = 0,
    check_sorted: bool = False,
    allow_empty_cells: bool = False,
    case_sensitive: bool = False,
) -> None:
    """Execute end-to-end quality gate validations on a tabular dataset.

    Args:
        table: Tabular dataset to validate.
        expected_columns: Optional exact column count constraint.
        key_index: Column index for uniqueness and sorting, or None.
        check_sorted: Whether to enforce alphabetical sorting.
        allow_empty_cells: Whether blank cell values are permitted.
        case_sensitive: Whether case differences are differentiated.

    Raises:
        DatasetSchemaError: If structural or cell invariants are violated.
        DuplicateEntryError: If duplicate entries or rows are detected.
        SortOrderError: If rows violate expected sort order.
    """
    validate_table_schema(
        table=table,
        expected_columns=expected_columns,
        allow_empty_cells=allow_empty_cells,
    )

    assert_no_duplicates(
        table=table,
        key_index=key_index,
        case_sensitive=case_sensitive,
    )

    if check_sorted and key_index is not None:
        assert_sorted_order(
            table=table,
            key_index=key_index,
            case_sensitive=case_sensitive,
        )
