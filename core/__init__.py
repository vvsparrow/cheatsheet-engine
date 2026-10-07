"""Core domain package for cheatsheet engine."""

from core.models import BoundingBox, Resolution, SafeZone, TableData
from core.presets import (
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
    DevicePreset,
)

__all__ = [
    "DESKTOP_2K",
    "IPAD_PORTRAIT",
    "LAPTOP_FHD",
    "PHONE_LOCKSCREEN",
    "PHONE_PANORAMA",
    "BoundingBox",
    "DevicePreset",
    "Resolution",
    "SafeZone",
    "TableData",
]
