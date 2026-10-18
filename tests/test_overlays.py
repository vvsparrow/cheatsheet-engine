"""Tests for device UI mockup overlays and frame simulations."""

from __future__ import annotations

import pytest
from PIL import Image

from core.overlays import apply_device_overlay
from core.presets import IPAD_PORTRAIT, LAPTOP_FHD, PHONE_LOCKSCREEN


def test_apply_device_overlay_mismatched_resolution_raises() -> None:
    """Ensure ValueError is raised when image size does not match preset."""
    img = Image.new("RGB", (800, 600), color=(18, 20, 24))

    with pytest.raises(ValueError, match=r"Image dimensions.*do not match"):
        apply_device_overlay(image=img, preset=LAPTOP_FHD)


def test_apply_device_overlay_preserves_dimensions_and_mode() -> None:
    """Ensure applied overlay returns new RGB image with identical size."""
    orig = Image.new(
        "RGB",
        (LAPTOP_FHD.resolution.width, LAPTOP_FHD.resolution.height),
        color=(18, 20, 24),
    )
    result = apply_device_overlay(image=orig, preset=LAPTOP_FHD)

    assert result.size == (
        LAPTOP_FHD.resolution.width,
        LAPTOP_FHD.resolution.height,
    )
    assert result.mode == "RGB"
    assert result is not orig


def test_apply_device_overlay_lockscreen_draws_ui_elements() -> None:
    """Ensure lockscreen overlay renders UI elements in upper safe zone."""
    w, h = (
        PHONE_LOCKSCREEN.resolution.width,
        PHONE_LOCKSCREEN.resolution.height,
    )
    orig = Image.new("RGB", (w, h), color=(18, 20, 24))
    result = apply_device_overlay(image=orig, preset=PHONE_LOCKSCREEN)

    # Upper region (clock/date) must contain rendered UI pixels
    # distinct from the background color (18, 20, 24).
    clock_y = int(h * 0.18)
    center_x = w // 2
    box_crop = result.crop((center_x - 50, clock_y - 20, center_x + 50, clock_y + 20))
    colors = box_crop.getcolors(maxcolors=256)
    assert colors is not None and len(colors) > 1


def test_apply_device_overlay_desktop_draws_taskbar() -> None:
    """Ensure desktop overlay renders taskbar at the bottom of the screen."""
    w, h = (LAPTOP_FHD.resolution.width, LAPTOP_FHD.resolution.height)
    orig = Image.new("RGB", (w, h), color=(18, 20, 24))
    result = apply_device_overlay(image=orig, preset=LAPTOP_FHD)

    # Bottom taskbar area (last 48px) must contain modified pixels
    taskbar_crop = result.crop((0, h - 48, w, h))
    colors = taskbar_crop.getcolors(maxcolors=256)
    assert colors is not None and len(colors) > 1


def test_apply_device_overlay_ipad_draws_status_and_home_bar() -> None:
    """Ensure iPad overlay renders status bar up top and home bar at bottom."""
    w, h = (IPAD_PORTRAIT.resolution.width, IPAD_PORTRAIT.resolution.height)
    orig = Image.new("RGB", (w, h), color=(18, 20, 24))
    result = apply_device_overlay(image=orig, preset=IPAD_PORTRAIT)

    # Top status bar region (within top 100px) must contain rendered UI pixels
    top_crop = result.crop((0, 0, w, 100))
    top_colors = top_crop.getcolors(maxcolors=65536)
    assert top_colors is not None and len(top_colors) > 1

    # Bottom Home Indicator region (last 50px) must contain rendered UI pixels
    bottom_crop = result.crop((0, h - 50, w, h))
    bottom_colors = bottom_crop.getcolors(maxcolors=65536)
    assert bottom_colors is not None and len(bottom_colors) > 1
