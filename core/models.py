"""Domain models for device screen geometry and layout safe zones."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Resolution:
    """Screen resolution in physical pixels.

    Attributes:
        width: Width in pixels (must be positive).
        height: Height in pixels (must be positive).
    """

    width: int
    height: int

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio (width / height)."""
        return self.width / self.height

    def get_safe_area(self, safe_zone: SafeZone) -> BoundingBox:
        """Calculate the usable content bounding box within safe margins.

        Args:
            safe_zone: Safe zone padding to subtract  from boundaries.

        Returns:
            BoundingBox representing the usable drawing area.
        """
        usable_width = self.width - (safe_zone.left + safe_zone.right)
        usable_height = self.height - (safe_zone.top + safe_zone.bottom)
        return BoundingBox(
            x=safe_zone.left,
            y=safe_zone.top,
            width=usable_width,
            height=usable_height,
        )


@dataclass(frozen=True, slots=True)
class SafeZone:
    """Safe zone padding to prevent UI clipping by system elements.

    Attributes:
        top: Padding from top edge in pixels.
        bottom: Padding from bottom edge in pixels.
        left: Padding from left edge in pixels.
        right: Padding from right edge in pixels.
    """

    top: int
    bottom: int
    left: int
    right: int


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-Aligned Bounding Box representing a rectangular layout area.

    Attributes:
        x: Top-left X coordinate in pixels.
        y: Top-left Y coordinate in pixels.
        width: Width in pixels (must be positive).
        height: Height in pixels (must be positive).
    """

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        """Validate box dimensions."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("BoundingBox width and height must be strictly positive.")

    @property
    def right(self) -> int:
        """Calculate right boundary X coordinate."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Calculate bottom boundary Y coordinate."""
        return self.y + self.height


@dataclass(frozen=True, slots=True)
class TableData:
    """Arbitrary tabular dataset schema with shape validation.

    Attributes:
        headers: Column header names.
        rows: Row entries matching header column count.
    """

    headers: Sequence[str]
    rows: Sequence[Sequence[str]]

    def __post_init__(self) -> None:
        """Validate tabular structure and enforce immutable tuples."""
        if not self.headers:
            raise ValueError("Headers cannot be empty.")

        normalized_headers = tuple(self.headers)
        normalized_rows = tuple(tuple(row) for row in self.rows)

        col_count = len(normalized_headers)
        for row in normalized_rows:
            if len(row) != col_count:
                raise ValueError(
                    "Row length mismatch: every row must match column count."
                )

        object.__setattr__(self, "headers", normalized_headers)
        object.__setattr__(self, "rows", normalized_rows)

    @property
    def column_count(self) -> int:
        """Return total number of columns."""
        return len(self.headers)

    @property
    def row_count(self) -> int:
        """Return total number of rows."""
        return len(self.rows)
