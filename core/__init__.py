"""Core domain package for cheatsheet engine."""

from __future__ import annotations

from core.engine import (
    calculate_column_widths,
    calculate_layout_boxes,
    calculate_rows_per_page,
    get_font,
    render_wallpaper,
)
from core.geometry import (
    LayoutCollisionError,
    SafeZoneViolationError,
    assert_no_collisions,
    assert_within_safe_area,
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
    "LayoutCollisionError",
    "Resolution",
    "SafeZone",
    "SafeZoneViolationError",
    "TableData",
    "assert_no_collisions",
    "assert_within_safe_area",
    "calculate_column_widths",
    "calculate_layout_boxes",
    "calculate_rows_per_page",
    "get_font",
    "render_wallpaper",
]
