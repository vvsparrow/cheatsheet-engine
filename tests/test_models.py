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
