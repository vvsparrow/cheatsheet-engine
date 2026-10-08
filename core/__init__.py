"""Core domain package for cheatsheet engine."""

from __future__ import annotations

from core.engine import (
    calculate_column_widths,
    calculate_rows_per_page,
    get_font,
    render_wallpaper,
)
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
    "calculate_column_widths",
    "calculate_rows_per_page",
    "get_font",
    "render_wallpaper",
]
