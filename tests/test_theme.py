"""Unit tests for theme configurations, tokens, and registry retrieval."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.theme import (
    CLINICAL_THEME,
    DARK_THEME,
    LIGHT_THEME,
    THEMES,
    TOKYO_NIGHT_THEME,
    Theme,
    get_theme,
)


def test_theme_immutability() -> None:
    """Ensure Theme dataclass is frozen and prevents attribute mutations."""
    theme = DARK_THEME
    with pytest.raises(FrozenInstanceError):
        theme.background = (0, 0, 0)  # type: ignore[misc]


def test_get_theme_returns_expected_instances() -> None:
    """Ensure get_theme retrieves canonical theme instances."""
    assert get_theme("dark") is DARK_THEME
    assert get_theme("light") is LIGHT_THEME
    assert get_theme("clinical") is CLINICAL_THEME
    assert get_theme("tokyo-night") is TOKYO_NIGHT_THEME


def test_get_theme_normalizes_case_and_whitespace() -> None:
    """Ensure get_theme strips whitespace and handles uppercase input."""
    assert get_theme("  DARK  ") is DARK_THEME
    assert get_theme("CLINICAL") is CLINICAL_THEME
    assert get_theme("Tokyo-Night") is TOKYO_NIGHT_THEME


def test_get_theme_raises_keyerror_on_unknown_theme() -> None:
    """Ensure get_theme raises descriptive KeyError for unregistered theme."""
    with pytest.raises(KeyError, match="Unknown theme 'matrix'"):
        get_theme("matrix")


@pytest.mark.parametrize(
    "theme",
    [DARK_THEME, LIGHT_THEME, CLINICAL_THEME, TOKYO_NIGHT_THEME],
)
def test_theme_color_channels_within_valid_rgb_range(theme: Theme) -> None:
    """Ensure all color tokens consist of valid 8-bit RGB channels."""
    channels = [
        theme.background,
        theme.row_alt,
        theme.text_primary,
        theme.text_header,
        theme.separator,
    ]
    for channel in channels:
        assert len(channel) == 3
        for val in channel:
            assert 0 <= val <= 255


def test_themes_registry_contains_all_four_themes() -> None:
    """Ensure THEMES registry exposes exactly the four curated presets."""
    assert set(THEMES.keys()) == {"clinical", "dark", "light", "tokyo-night"}
