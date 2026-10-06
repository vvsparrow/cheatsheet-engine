"""Unit tests for domain models (Resolution, SafeZone)."""

from dataclasses import FrozenInstanceError

import pytest

from core import Resolution, SafeZone


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
