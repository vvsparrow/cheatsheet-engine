"""Architectural metrics, typography proportions, and layout constants."""

from __future__ import annotations

__all__ = [
    "CELL_MIN_TEXT_WIDTH",
    "CELL_PAD_X",
    "CELL_PAD_X_TOTAL",
    "DEFAULT_ADAPTIVE_LINE_RATIO",
    "DEFAULT_GUTTER",
    "DEFAULT_MAX_FONT_SIZE",
    "HEADER_LINE_OFFSET_MIN",
    "HEADER_SPACER_MIN",
    "HEADER_SPACER_RATIO",
    "LINE_STEP_RATIO",
    "ROW_PAD_Y_MIN",
    "ROW_PAD_Y_RATIO",
]

# Cell horizontal insets and boundary limits
CELL_PAD_X: int = 10
CELL_PAD_X_TOTAL: int = 20
CELL_MIN_TEXT_WIDTH: int = 10

# Vertical text line rhythm and cell row padding
LINE_STEP_RATIO: float = 1.45
ROW_PAD_Y_MIN: int = 3
ROW_PAD_Y_RATIO: float = 0.2

# Header section metrics and vertical dividers
HEADER_LINE_OFFSET_MIN: int = 18
HEADER_SPACER_MIN: int = 8
HEADER_SPACER_RATIO: float = 0.5

# Multi-block layout spacing and typography scaling bounds
DEFAULT_GUTTER: int = 24
DEFAULT_MAX_FONT_SIZE: int = 24
DEFAULT_ADAPTIVE_LINE_RATIO: float = 1.55
