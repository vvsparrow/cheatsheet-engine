"""Geometry validation and Quality Gates assertions for layout rendering."""

from __future__ import annotations

from collections.abc import Sequence

from core.models import BoundingBox


class LayoutCollisionError(AssertionError):
    """Raised when two or more layout elements overlap on canvas."""


class SafeZoneViolationError(AssertionError):
    """Raised when a layout element exceeds designated safe area boundaries."""


def assert_no_collisions(boxes: Sequence[BoundingBox]) -> None:
    """Ensure no two bounding boxes in the sequence overlap.

    Args:
        boxes: Sequence of layout BoundingBox instances to verify.

    Raises:
        LayoutCollisionError: If any pair of boxes strictly intersects.
    """
    total = len(boxes)
    for i in range(total):
        for j in range(i + 1, total):
            if boxes[i].intersects(boxes[j]):
                raise LayoutCollisionError(
                    f"Layout collision detected between box[{i}] ({boxes[i]}) and box [{j}] ({boxes[j]})."
                )


def assert_within_safe_area(
    boxes: Sequence[BoundingBox],
    safe_area: BoundingBox,
) -> None:
    """Ensure every bounding box strictly resides within the safe area.

    Args:
        boxes: Sequence of layout BoundingBox instances to verify.
        safe_area: Permissible boundary BoundingBox.

    Raises:
        SafeZoneViolationError: If any box extends outside the safe area.
    """
    for idx, box in enumerate(boxes):
        if not safe_area.contains(box):
            raise SafeZoneViolationError(
                f"Element box[{idx}] ({box}) exceeds safe area boundaries ({safe_area})."
            )
