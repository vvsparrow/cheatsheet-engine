"""Simulated device UI mockup overlays for visual layout verification."""

from __future__ import annotations

from PIL import Image, ImageDraw

from core.fonts import get_font
from core.presets import (
    DESKTOP_2K,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    DevicePreset,
)

__all__ = ["apply_device_overlay"]


def _draw_desktop_taskbar(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    bar_height: int = 48,
) -> None:
    """Render simulated OS bottom taskbar with start button and tray clock."""
    y_top = height - bar_height
    # Semi-transparent dark taskbar background
    draw.rectangle(
        [(0, y_top), (width, height)],
        fill=(18, 22, 28, 225),
    )
    # Subtle accent top border
    draw.line(
        [(0, y_top), (width, y_top)],
        fill=(80, 95, 115, 160),
        width=1,
    )
    # Start button indicator (bottom-left)
    draw.rounded_rectangle(
        [(16, y_top + 10), (44, height - 10)],
        radius=4,
        fill=(60, 140, 240, 200),
    )
    # Tray clock text (bottom-right)
    tray_font = get_font(size=13, bold=False)
    draw.text(
        (width - 65, y_top + 16),
        "12:00",
        fill=(220, 225, 235, 210),
        font=tray_font,
    )


def _draw_phone_lockscreen_ui(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
) -> None:
    """Render simulated mobile lockscreen UI: clock, dynamic island, home bar."""
    center_x = width // 2

    # Dynamic Island / Camera cutout
    island_w = int(width * 0.28)
    island_h = int(height * 0.013)
    island_y = int(height * 0.016)
    draw.rounded_rectangle(
        [
            (center_x - island_w // 2, island_y),
            (center_x + island_w // 2, island_y + island_h),
        ],
        radius=island_h // 2,
        fill=(0, 0, 0, 250),
    )

    # Date header
    date_font = get_font(size=int(height * 0.014), bold=False)
    date_text = "Wednesday, September 16"
    draw.text(
        (center_x, int(height * 0.125)),
        date_text,
        fill=(240, 240, 245, 220),
        font=date_font,
        anchor="mt",
    )

    # Large Lockscreen Clock (09:41)
    clock_font = get_font(size=int(height * 0.065), bold=True)
    draw.text(
        (center_x, int(height * 0.155)),
        "09:41",
        fill=(245, 245, 250, 235),
        font=clock_font,
        anchor="mt",
    )

    # Bottom Home Indicator Bar
    bar_w = int(width * 0.36)
    bar_h = max(4, int(height * 0.002))
    bar_y = height - int(height * 0.012)
    draw.rounded_rectangle(
        [
            (center_x - bar_w // 2, bar_y),
            (center_x + bar_w // 2, bar_y + bar_h),
        ],
        radius=bar_h // 2,
        fill=(255, 255, 255, 180),
    )


def _draw_panorama_dividers(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
) -> None:
    """Render vertical screen fold dividers for phone panorama swipe preview."""
    panel_w = width // 3
    for fold_x in (panel_w, panel_w * 2):
        draw.line(
            [(fold_x, 0), (fold_x, height)],
            fill=(100, 200, 255, 90),
            width=2,
        )


def apply_device_overlay(
    image: Image.Image,
    preset: DevicePreset,
) -> Image.Image:
    """Apply simulated device OS interface elements over wallpaper image.

    Args:
        image: Base wallpaper image to composite overlay onto.
        preset: Target device preset providing resolution and geometry context.

    Returns:
        New RGB Image instance composited with simulated OS elements.

    Raises:
        ValueError: If image dimensions do not match preset resolution.
    """
    if (image.width, image.height) != (
        preset.resolution.width,
        preset.resolution.height,
    ):
        raise ValueError(
            f"Image dimensions ({image.width}x{image.height}) do not match "
            f"preset resolution ({preset.resolution.width}x"
            f"{preset.resolution.height})."
        )

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if preset in (DESKTOP_2K, LAPTOP_FHD):
        _draw_desktop_taskbar(draw=draw, width=image.width, height=image.height)
    elif preset == PHONE_LOCKSCREEN:
        _draw_phone_lockscreen_ui(draw=draw, width=image.width, height=image.height)

    base = image.convert("RGBA")
    composited = Image.alpha_composite(base, overlay)
    return composited.convert("RGB")
