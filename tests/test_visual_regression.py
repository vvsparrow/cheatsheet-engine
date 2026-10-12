"""Automated visual regression tests validating rendered wallpapers."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from PIL import Image

from core.engine import render_wallpaper
from core.models import TableData
from core.presets import DESKTOP_2K, LAPTOP_FHD, PHONE_LOCKSCREEN

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Visual golden snapshots are calibrated against Linux FreeType rasterization",
)

FIXED_DATASET = TableData(
    headers=["Command", "Description"],
    rows=[
        ["git status", "Show working tree status"],
        ["git diff", "Show changes between commits"],
        ["git commit", "Record changes to repository"],
        ["git push", "Update remote refs along with objects"],
        ["git pull", "Fetch from and integrate with remote"],
        ["git checkout", "Switch branches or restore files"],
    ],
)


def test_visual_regression_laptop_fhd(
    tmp_path: Path,
    assert_snapshot: Callable[[Image.Image, str, float], None],
) -> None:
    """Ensure LAPTOP_FHD matches golden baseline without layout shifts."""
    out_file = tmp_path / "laptop_fhd_actual.png"
    render_wallpaper(table=FIXED_DATASET, preset=LAPTOP_FHD, output_path=out_file)

    actual_img = Image.open(out_file)
    assert_snapshot(actual_img, "laptop_fhd_baseline.png", 0.01)


def test_visual_regression_desktop_2k(
    tmp_path: Path,
    assert_snapshot: Callable[[Image.Image, str, float], None],
) -> None:
    """Ensure DESKTOP_2K matches golden baseline without layout shifts."""
    out_file = tmp_path / "desktop_2k_actual.png"
    render_wallpaper(table=FIXED_DATASET, preset=DESKTOP_2K, output_path=out_file)

    actual_img = Image.open(out_file)
    assert_snapshot(actual_img, "desktop_2k_baseline.png", 0.01)


def test_visual_regression_phone_lockscreen(
    tmp_path: Path,
    assert_snapshot: Callable[[Image.Image, str, float], None],
) -> None:
    """Ensure PHONE_LOCKSCREEN matches golden baseline without layout shifts."""
    out_file = tmp_path / "phone_lockscreen_actual.png"
    render_wallpaper(table=FIXED_DATASET, preset=PHONE_LOCKSCREEN, output_path=out_file)

    actual_img = Image.open(out_file)
    assert_snapshot(actual_img, "phone_lockscreen_baseline.png", 0.01)


def test_visual_regression_catches_layout_shift(
    tmp_path: Path,
    assert_snapshot: Callable[[Image.Image, str, float], None],
) -> None:
    """Ensure mutated dataset triggers visual regression assertion error."""
    mutated_dataset = TableData(
        headers=["Command", "Modified Description Header"],
        rows=FIXED_DATASET.rows,
    )
    out_file = tmp_path / "mutated_actual.png"
    render_wallpaper(table=mutated_dataset, preset=LAPTOP_FHD, output_path=out_file)

    actual_img = Image.open(out_file)
    with pytest.raises(AssertionError, match="Visual regression detected"):
        assert_snapshot(actual_img, "laptop_fhd_baseline.png", 0.01)
