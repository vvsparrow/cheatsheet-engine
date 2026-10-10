"""Tests for geometric assertions and layout quality gates."""

from __future__ import annotations

import pytest

from core.geometry import (
    LayoutCollisionError,
    SafeZoneViolationError,
    assert_no_collisions,
    assert_within_safe_area,
)
from core.layout import calculate_layout_boxes
from core.models import BoundingBox, TableData
from core.presets import (
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
    DevicePreset,
)

ALL_PRESETS: tuple[DevicePreset, ...] = (
    DESKTOP_2K,
    LAPTOP_FHD,
    IPAD_PORTRAIT,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
)


def test_assert_no_collisions_passes_for_disjoint_boxes() -> None:
    """Ensure assert_no_collisions does not raise for separated boxes."""
    boxes = (
        BoundingBox(x=10, y=10, width=50, height=20),
        BoundingBox(x=70, y=10, width=50, height=20),
        BoundingBox(x=10, y=40, width=50, height=20),
    )
    assert_no_collisions(boxes)


def test_assert_no_collisions_raises_on_overlap() -> None:
    """Ensure assert_no_collisions raises LayoutCollisionError on overlap."""
    boxes = (
        BoundingBox(x=10, y=10, width=50, height=50),
        BoundingBox(x=30, y=30, width=50, height=50),
    )
    with pytest.raises(LayoutCollisionError, match="collision detected"):
        assert_no_collisions(boxes)


def test_assert_within_safe_area_passes_when_contained() -> None:
    """Ensure assert_within_safe_area passes when all boxes are enclosed."""
    safe_area = BoundingBox(x=0, y=0, width=1000, height=1000)
    boxes = (
        BoundingBox(x=0, y=0, width=100, height=50),
        BoundingBox(x=200, y=200, width=300, height=100),
    )
    assert_within_safe_area(boxes=boxes, safe_area=safe_area)


def test_assert_within_safe_area_raises_when_out_of_bounds() -> None:
    """Ensure assert_within_safe_area raises SafeZoneViolationError."""
    safe_area = BoundingBox(x=50, y=50, width=200, height=200)
    boxes = (
        BoundingBox(x=10, y=50, width=50, height=50),  # x < safe_area.x
    )
    with pytest.raises(SafeZoneViolationError, match="exceeds safe area"):
        assert_within_safe_area(boxes=boxes, safe_area=safe_area)


@pytest.mark.parametrize("preset", ALL_PRESETS)
def test_layout_quality_gates_across_all_presets(preset: DevicePreset) -> None:
    """Ensure rendered layout all quality gates for each preset."""
    table = TableData(
        headers=["Col 1", "Col 2"],
        rows=[["Row 1 Col 1", "Row 1 Col 2"], ["Row 2 Col 1", "Row 2 Col 2"]],
    )
    boxes = calculate_layout_boxes(table=table, preset=preset, page=1)
    safe_area = preset.get_safe_area()

    assert_no_collisions(boxes)
    assert_within_safe_area(boxes=boxes, safe_area=safe_area)
