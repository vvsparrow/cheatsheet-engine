"""Theme definitions and WCAG-compliant color palettes."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "CLINICAL_THEME",
    "DARK_THEME",
    "LIGHT_THEME",
    "THEMES",
    "TOKYO_NIGHT_THEME",
    "Theme",
    "get_theme",
]


@dataclass(frozen=True, slots=True)
class Theme:
    """Immutable color palette and visual tokens for canvas rendering.

    Attributes:
        name: Unique lowercase identifier of the theme.
        background: Canvas primary fill color in 8-bit RGB.
        row_alt: Alternate row zebra striping fill color in 8-bit RGB.
        text_primary: Main tabular data body text fill color in 8-bit RGB.
        text_header: Table column header label fill color in 8-bit RGB.
        separator: Horizontal header divider line stroke color in 8-bit RGB.
    """

    name: str
    background: tuple[int, int, int]
    row_alt: tuple[int, int, int]
    text_primary: tuple[int, int, int]
    text_header: tuple[int, int, int]
    separator: tuple[int, int, int]


DARK_THEME = Theme(
    name="dark",
    background=(18, 20, 24),
    row_alt=(26, 29, 36),
    text_primary=(240, 240, 240),
    text_header=(100, 200, 255),
    separator=(100, 200, 255),
)

LIGHT_THEME = Theme(
    name="light",
    background=(248, 250, 252),
    row_alt=(241, 245, 249),
    text_primary=(15, 23, 42),
    text_header=(2, 132, 199),
    separator=(2, 132, 199),
)

CLINICAL_THEME = Theme(
    name="clinical",
    background=(15, 23, 42),
    row_alt=(30, 41, 59),
    text_primary=(241, 245, 249),
    text_header=(56, 189, 248),
    separator=(56, 189, 248),
)

TOKYO_NIGHT_THEME = Theme(
    name="tokyo-night",
    background=(26, 27, 38),
    row_alt=(36, 40, 59),
    text_primary=(192, 202, 245),
    text_header=(122, 162, 247),
    separator=(122, 162, 247),
)

THEMES: dict[str, Theme] = {
    "clinical": CLINICAL_THEME,
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "tokyo-night": TOKYO_NIGHT_THEME,
}


def get_theme(name: str = "dark") -> Theme:
    """Retrieve a theme configuration by its canonical name.

    Args:
        name: Name of the theme ('dark', 'light', 'clinical', 'tokyo-night').

    Returns:
        Theme instance corresponding to the given name.

    Raises:
        KeyError: If requested theme name is not registered.
    """
    normalized = name.strip().lower()
    if normalized not in THEMES:
        available = ", ".join(sorted(THEMES.keys()))
        raise KeyError(f"Unknown theme '{name}'. Available themes: {available}.")
    return THEMES[normalized]
