"""Tests for device layout presets and geometry invariants."""

from __future__ import annotations

import pytest

from core.models import Resolution, SafeZone
from core.presets import (
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
    DevicePreset,
)

ALL_PRESETS = [
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
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
    """Validate Phone Lockscreen specific safe zone padding (38% top, 15% bottom)."""
    assert PHONE_LOCKSCREEN.resolution.width == 1290
    assert PHONE_LOCKSCREEN.resolution.height == 2796
    expected_top = int(2796 * 0.38)
    expected_bottom = int(2796 * 0.15)
    assert PHONE_LOCKSCREEN.safe_zone.top == expected_top
    assert PHONE_LOCKSCREEN.safe_zone.bottom == expected_bottom


def test_desktop_and_tablet_safe_zones_reserve_system_margins() -> None:
    """Ensure desktop and tablet presets reserve space for icons and bars."""
    assert DESKTOP_2K.safe_zone.left >= 200
    assert DESKTOP_2K.safe_zone.bottom >= 60
    assert LAPTOP_FHD.safe_zone.left >= 100
    assert LAPTOP_FHD.safe_zone.bottom >= 50
    assert IPAD_PORTRAIT.safe_zone.top >= 150
