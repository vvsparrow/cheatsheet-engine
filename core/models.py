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


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-Aligned Bounding Box representing a rectangular layout area.

    Attributes:
        x: Top-left X coordinate in pixels.
        y: Top-left Y coordinate in pixels.
        width: Width in pixels (must be positive).
        height: Height in pixels (must be positive).
    """

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        """Validate box dimensions."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("BoundingBox width and height must be strictly positive.")

    @property
    def right(self) -> int:
        """Calculate right boundary X coordinate."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Calculate bottom boundary Y coordinate."""
        return self.y + self.height
