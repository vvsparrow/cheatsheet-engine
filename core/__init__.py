"""Core domain package for cheatsheet engine."""

from __future__ import annotations

from core.engine import render_wallpaper
from core.fonts import get_font
from core.geometry import (
    LayoutCollisionError,
    SafeZoneViolationError,
    assert_no_collisions,
    assert_within_safe_area,
)
from core.layout import (
    calculate_column_widths,
    calculate_layout_boxes,
    calculate_rows_per_page,
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
from core.typography import (
    calculate_line_height,
    truncate_to_width,
    wrap_text,
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
    "calculate_line_height",
    "calculate_rows_per_page",
    "get_font",
    "render_wallpaper",
    "truncate_to_width",
    "wrap_text",
]
