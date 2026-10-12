"""Core domain package for cheatsheet engine."""

from __future__ import annotations

from core.anki import AnkiCardMapping, compile_anki_deck
from core.boxes import calculate_layout_boxes
from core.columns import (
    calculate_column_widths,
    calculate_rows_per_page,
)
from core.engine import render_wallpaper
from core.fonts import get_font
from core.geometry import (
    LayoutCollisionError,
    SafeZoneViolationError,
    assert_no_collisions,
    assert_within_safe_area,
)
from core.layout import (
    calculate_page_capacity,
)
from core.models import BoundingBox, Resolution, SafeZone, TableData
from core.observability import MetricsCollector, RenderReport, get_logger
from core.overlays import apply_device_overlay
from core.packager import create_bundle_pack
from core.presets import (
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
    DevicePreset,
)
from core.series import render_card_pack
from core.theme import (
    CLINICAL_THEME,
    DARK_THEME,
    LIGHT_THEME,
    TOKYO_NIGHT_THEME,
    Theme,
    get_theme,
)
from core.typography import (
    calculate_line_height,
    truncate_to_width,
    wrap_text,
)
from core.validation import (
    DatasetSchemaError,
    DatasetValidationError,
    DuplicateEntryError,
    SortOrderError,
    assert_no_duplicates,
    assert_sorted_order,
    validate_dataset,
    validate_table_schema,
)

__all__ = [
    "CLINICAL_THEME",
    "DARK_THEME",
    "DESKTOP_2K",
    "IPAD_PORTRAIT",
    "LAPTOP_FHD",
    "LIGHT_THEME",
    "PHONE_LOCKSCREEN",
    "PHONE_PANORAMA",
    "TOKYO_NIGHT_THEME",
    "AnkiCardMapping",
    "BoundingBox",
    "DatasetSchemaError",
    "DatasetValidationError",
    "DevicePreset",
    "DuplicateEntryError",
    "LayoutCollisionError",
    "MetricsCollector",
    "RenderReport",
    "Resolution",
    "SafeZone",
    "SafeZoneViolationError",
    "SortOrderError",
    "TableData",
    "Theme",
    "apply_device_overlay",
    "assert_no_collisions",
    "assert_no_duplicates",
    "assert_sorted_order",
    "assert_within_safe_area",
    "calculate_column_widths",
    "calculate_layout_boxes",
    "calculate_line_height",
    "calculate_page_capacity",
    "calculate_rows_per_page",
    "compile_anki_deck",
    "create_bundle_pack",
    "get_font",
    "get_logger",
    "get_theme",
    "render_card_pack",
    "render_wallpaper",
    "truncate_to_width",
    "validate_dataset",
    "validate_table_schema",
    "wrap_text",
]
