"""Standard device layout presets and configurations."""

from __future__ import annotations

from dataclasses import dataclass

from core.models import BoundingBox, Resolution, SafeZone

__all__ = [
    "DESKTOP_2K",
    "IPAD_PORTRAIT",
    "LAPTOP_FHD",
    "PHONE_LOCKSCREEN",
    "PHONE_PANORAMA",
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

    def get_safe_area(self) -> BoundingBox:
        """Calculate the usable content area within safe margins."""
        return self.resolution.get_safe_area(self.safe_zone)


DESKTOP_2K = DevicePreset(
    name="Desktop 2K",
    resolution=Resolution(width=2560, height=1440),
    safe_zone=SafeZone(top=0, bottom=0, left=0, right=0),
)

LAPTOP_FHD = DevicePreset(
    name="Laptop Full HD",
    resolution=Resolution(width=1920, height=1080),
    safe_zone=SafeZone(top=0, bottom=0, left=0, right=0),
)

IPAD_PORTRAIT = DevicePreset(
    name="iPad Portrait",
    resolution=Resolution(width=2048, height=2732),
    safe_zone=SafeZone(top=0, bottom=0, left=0, right=0),
)

PHONE_PANORAMA = DevicePreset(
    name="Phone Panorama",
    resolution=Resolution(width=3240, height=2412),
    safe_zone=SafeZone(top=0, bottom=0, left=0, right=0),
)

PHONE_LOCKSCREEN = DevicePreset(
    name="Phone Lockscreen",
    resolution=Resolution(width=1290, height=2796),
    safe_zone=SafeZone(
        top=int(2796 * 0.38),
        bottom=int(2796 * 0.15),
        left=0,
        right=0,
    ),
)
