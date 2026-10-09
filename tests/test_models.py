"""Unit tests for domain models (Resolution, SafeZone)."""

from dataclasses import FrozenInstanceError

import pytest

from core import BoundingBox, Resolution, SafeZone


def test_resolution_creation() -> None:
    """Ensure Resolution stores width and height correctly."""
    res = Resolution(width=2048, height=2732)
    assert res.width == 2048
    assert res.height == 2732


def test_resolution_aspect_ratio() -> None:
    """Ensure aspect_ratio correctly calculates width divided by height."""
    res = Resolution(width=1920, height=1080)
    assert res.aspect_ratio == pytest.approx(1920 / 1080)


def test_resolution_immutability() -> None:
    """Ensure Resolution cannot be mutated (frozen dataclass)."""
    res = Resolution(width=2048, height=2732)
    with pytest.raises(FrozenInstanceError):
        res.width = 1000  # type: ignore


def test_safe_zone_creation_and_immutability() -> None:
    """Ensure SafeZone correctly stores padding and is immutable."""
    sz = SafeZone(top=40, bottom=40, left=20, right=20)
    assert sz.top == 40
    assert sz.bottom == 40
    assert sz.left == 20
    assert sz.right == 20

    with pytest.raises(FrozenInstanceError):
        sz.top = 100  # type: ignore


def test_bounding_box_creation_and_boundaries() -> None:
    """Ensure BoundingBox calculates right and bottom boundaries."""
    box = BoundingBox(x=100, y=150, width=800, height=600)
    assert box.x == 100
    assert box.y == 150
    assert box.width == 800
    assert box.height == 600
    assert box.right == 900
    assert box.bottom == 750


def test_bounding_box_invalid_dimensions_raise_error() -> None:
    """Ensure BoundingBox rejects non-positive dimensions."""
    with pytest.raises(ValueError, match="strictly positive"):
        BoundingBox(x=0, y=0, width=0, height=100)

    with pytest.raises(ValueError, match="strictly positive"):
        BoundingBox(x=0, y=0, width=100, height=-5)


def test_bounding_box_immutability() -> None:
    """Ensure BoundingBox cannot be mutated (frozen dataclass)."""
    box = BoundingBox(x=10, y=10, width=100, height=100)
    with pytest.raises(FrozenInstanceError):
        box.x = 50  #  type: ignore


def test_resolution_get_safe_area_valid() -> None:
    """Ensure get_safe_area computes correct usable BoundingBox."""
    res = Resolution(width=1920, height=1080)
    sz = SafeZone(top=80, bottom=80, left=120, right=120)
    box = res.get_safe_area(sz)

    assert box.x == 120
    assert box.y == 80
    assert box.width == 1680
    assert box.height == 920


def test_resolution_get_safe_area_exceeds_dimensions() -> None:
    """Ensure get_safe_area raises ValueError if safe zone exceeds canvas."""
    res = Resolution(width=100, height=100)
    sz = SafeZone(top=60, bottom=50, left=10, right=10)

    with pytest.raises(ValueError, match="strictly positive"):
        res.get_safe_area(sz)


def test_bounding_box_intersects_overlapping() -> None:
    """Ensure intersects returns True for overlapping bounding boxes."""
    box_a = BoundingBox(x=10, y=10, width=50, height=50)
    box_b = BoundingBox(x=30, y=30, width=50, height=50)
    assert box_a.intersects(box_b) is True
    assert box_b.intersects(box_a) is True


def test_bounding_box_intersects_separated() -> None:
    """Ensure intersects returns False for separated bounding boxes."""
    box_a = BoundingBox(x=10, y=10, width=20, height=20)
    box_b = BoundingBox(x=50, y=50, width=20, height=20)
    assert box_a.intersects(box_b) is False
    assert box_b.intersects(box_a) is False


def test_bounding_box_intersects_touching_edges() -> None:
    """Ensure adjacent boxes sharing an edge do not count as intersecting."""
    box_a = BoundingBox(x=0, y=0, width=10, height=10)
    box_b = BoundingBox(x=10, y=0, width=10, height=10)
    box_c = BoundingBox(x=0, y=10, width=10, height=10)
    assert box_a.intersects(box_b) is False
    assert box_a.intersects(box_c) is False


def test_bounding_box_contains_inner_box() -> None:
    """Ensure contains returns True when a box is completely enclosed."""
    outer = BoundingBox(x=0, y=0, width=100, height=100)
    inner = BoundingBox(x=10, y=10, width=80, height=80)
    assert outer.contains(inner) is True
    assert inner.contains(outer) is False


def test_bounding_box_contains_identical_and_flush_edges() -> None:
    """Ensure contains returns True for identical bounds or flush edges."""
    box_a = BoundingBox(x=0, y=0, width=100, height=100)
    box_b = BoundingBox(x=0, y=0, width=100, height=100)
    flush_inner = BoundingBox(x=0, y=0, width=50, height=50)
    assert box_a.contains(box_b) is True
    assert box_b.contains(flush_inner) is True


def test_bounding_box_contains_exceeding_boundaries() -> None:
    """Ensure contains returns False when a box extends outside boundaries."""
    outer = BoundingBox(x=10, y=10, width=50, height=50)
    partially_outside = BoundingBox(x=5, y=10, width=50, height=50)
    completely_outside = BoundingBox(x=100, y=100, width=20, height=20)
    assert outer.contains(partially_outside) is False
    assert outer.contains(completely_outside) is False
