"""Domain models for device screen geometry and layout safe zones."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Resolution:
    """Screen resolution in physical pixels.

    Attributes:
        width: Width in pixels (must be positive).
        height: Height in pixels (must be positive).
    """

    width: int
    height: int

    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio (width / height)."""
        return self.width / self.height


@dataclass(frozen=True, slots=True)
class SafeZone:
    """Safe zone padding to prevent UI clipping by system elements.

    Attributes:
        top: Padding from top edge in pixels.
        bottom: Padding from bottom edge in pixels.
        left: Padding from left edge in pixels.
        right: Padding from right edge in pixels.
    """

    top: int
    bottom: int
    left: int
    right: int
