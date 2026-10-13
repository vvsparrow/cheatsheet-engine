"""Standard device layout presets and configurations."""

from __future__ import annotations

from dataclasses import dataclass

from core.models import BoundingBox, Resolution, SafeZone

__all__ = [
    "DESKTOP_2K",
    "IPAD_PORTRAIT",
    "LAPTOP_FHD",
    "PHONE_LOCKSCREEN",
    "DevicePreset",
]


@dataclass(frozen=True, slots=True)
class DevicePreset:
    """Predefined device layout configuration.

    Attributes:
        name: Human-readable device preset name.
        resolution: Physical screen resolution.
        safe_zone: Padding margins for system UI elements.
    """

    name: str
    resolution: Resolution
    safe_zone: SafeZone
    font_size: int = 18
    row_height: int = 28

    def get_safe_area(self) -> BoundingBox:
        """Calculate the usable content area within safe margins."""
        return self.resolution.get_safe_area(self.safe_zone)


DESKTOP_2K = DevicePreset(
    name="Desktop 2K",
    resolution=Resolution(width=2560, height=1440),
    safe_zone=SafeZone(top=115, bottom=112, left=260, right=60),
)

LAPTOP_FHD = DevicePreset(
    name="Laptop Full HD",
    resolution=Resolution(width=1920, height=1080),
    safe_zone=SafeZone(top=80, bottom=112, left=120, right=50),
    font_size=14,
    row_height=21,
)

IPAD_PORTRAIT = DevicePreset(
    name="iPad Portrait",
    resolution=Resolution(width=2048, height=2732),
    safe_zone=SafeZone(top=280, bottom=80, left=80, right=80),
)


PHONE_LOCKSCREEN = DevicePreset(
    name="Phone Lockscreen",
    resolution=Resolution(width=1290, height=2796),
    safe_zone=SafeZone(
        top=int(2796 * 0.32),
        bottom=int(2796 * 0.12),
        left=int(1290 * 0.04),
        right=int(1290 * 0.04),
    ),
)
