"""Tests for device layout presets and geometry invariants."""

from __future__ import annotations

import pytest

from core.models import Resolution, SafeZone
from core.presets import (
    A4_LANDSCAPE,
    A4_PORTRAIT,
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    DevicePreset,
)

ALL_PRESETS = [
    A4_LANDSCAPE,
    A4_PORTRAIT,
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
]


@pytest.mark.parametrize("preset", ALL_PRESETS)
def test_preset_contract_invariants(preset: DevicePreset) -> None:
    """Ensure all presets have valid names, positive resolutions, and non-negative safe
    zones."""
    assert isinstance(preset.name, str) and len(preset.name) > 0
    assert isinstance(preset.resolution, Resolution)
    assert isinstance(preset.safe_zone, SafeZone)
    assert preset.resolution.width > 0
    assert preset.resolution.height > 0
    assert preset.safe_zone.top >= 0
    assert preset.safe_zone.bottom >= 0
    assert preset.safe_zone.left >= 0
    assert preset.safe_zone.right >= 0


@pytest.mark.parametrize("preset", ALL_PRESETS)
def test_preset_safe_area_computability(preset: DevicePreset) -> None:
    """Ensure safe area bounding box fits within physical screen resolution."""
    safe_area = preset.get_safe_area()
    assert safe_area.width > 0
    assert safe_area.height > 0
    assert safe_area.right <= preset.resolution.width
    assert safe_area.bottom <= preset.resolution.height


def test_phone_lockscreen_safe_zone_proportions() -> None:
    """Validate Phone Lockscreen safe margins (32% top, 12% bottom, 4% sides)."""
    assert PHONE_LOCKSCREEN.resolution.width == 1290
    assert PHONE_LOCKSCREEN.resolution.height == 2796
    expected_top = int(2796 * 0.32)
    expected_bottom = int(2796 * 0.12)
    expected_side = int(1290 * 0.04)

    assert PHONE_LOCKSCREEN.safe_zone.top == expected_top
    assert PHONE_LOCKSCREEN.safe_zone.bottom == expected_bottom
    assert PHONE_LOCKSCREEN.safe_zone.left == expected_side
    assert PHONE_LOCKSCREEN.safe_zone.right == expected_side


def test_desktop_and_tablet_safe_zones_reserve_system_margins() -> None:
    """Ensure desktop and tablet presets reserve space for icons and bars."""
    assert DESKTOP_2K.safe_zone.left >= 200
    assert DESKTOP_2K.safe_zone.bottom >= 60
    assert LAPTOP_FHD.safe_zone.left >= 100
    assert LAPTOP_FHD.safe_zone.bottom >= 50
    assert IPAD_PORTRAIT.safe_zone.top >= 150


def test_a4_presets_have_symmetric_margins_and_iso_resolution() -> None:
    """Ensure A4 print presets use symmetric 118px margins and 300 DPI resolutions."""
    assert A4_PORTRAIT.resolution.width == 2480
    assert A4_PORTRAIT.resolution.height == 3508
    assert A4_LANDSCAPE.resolution.width == 3508
    assert A4_LANDSCAPE.resolution.height == 2480

    for preset in (A4_PORTRAIT, A4_LANDSCAPE):
        assert preset.safe_zone.top == 118
        assert preset.safe_zone.bottom == 118
        assert preset.safe_zone.left == 118
        assert preset.safe_zone.right == 118
