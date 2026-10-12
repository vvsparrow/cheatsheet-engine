"""Tests for visual regression testing utilities and pixel-diff fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from tests.visual import assert_visual_snapshot, compare_images


def test_compare_images_identical_returns_zero_diff() -> None:
    """Ensure identical images return zero RMS difference and no diff mask."""
    img1 = Image.new("RGB", (100, 100), color=(18, 20, 24))
    img2 = Image.new("RGB", (100, 100), color=(18, 20, 24))

    rms, diff_mask = compare_images(actual=img1, expected=img2)

    assert rms == 0.0
    assert diff_mask is None


def test_compare_images_mismatched_dimensions_raises() -> None:
    """Ensure ValueError is raised when compared images have different sizes."""
    img1 = Image.new("RGB", (100, 100), color=(18, 20, 24))
    img2 = Image.new("RGB", (120, 100), color=(18, 20, 24))

    with pytest.raises(ValueError, match=r"Image dimensions.*do not match"):
        compare_images(actual=img1, expected=img2)


def test_compare_images_detects_one_pixel_difference() -> None:
    """Ensure a single modified pixel generates positive RMS and diff mask."""
    img1 = Image.new("RGB", (50, 50), color=(0, 0, 0))
    img2 = Image.new("RGB", (50, 50), color=(0, 0, 0))
    img1.putpixel((25, 25), (255, 255, 255))

    rms, diff_mask = compare_images(actual=img1, expected=img2)

    assert rms > 0.0
    assert diff_mask is not None
    assert diff_mask.size == (50, 50)


def test_assert_visual_snapshot_fails_and_writes_diff_artifacts(
    tmp_path: Path,
) -> None:
    """Ensure failing visual assertion writes actual and diff PNG artifacts."""
    expected_img = Image.new("RGB", (40, 40), color=(20, 20, 20))
    actual_img = Image.new("RGB", (40, 40), color=(200, 20, 20))

    golden_path = tmp_path / "golden_test.png"
    expected_img.save(golden_path)
    diff_dir = tmp_path / "diffs"

    with pytest.raises(AssertionError, match="Visual regression detected"):
        assert_visual_snapshot(
            actual=actual_img,
            golden_path=golden_path,
            threshold=0.01,
            diff_dir=diff_dir,
        )

    assert (diff_dir / "golden_test_actual.png").exists()
    assert (diff_dir / "golden_test_diff.png").exists()
