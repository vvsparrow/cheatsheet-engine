"""Visual regression testing utilities and pixel-diff analysis."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

__all__ = ["assert_visual_snapshot", "compare_images"]


def compare_images(
    actual: Image.Image,
    expected: Image.Image,
) -> tuple[float, Image.Image | None]:
    """Calculate Root-Mean-Square (RMS) error and optional visual diff mask.

    Args:
        actual: Rendered image to test.
        expected: Reference golden baseline image.

    Returns:
        Tuple of (rms_difference, diff_mask_image). If images are identical,
        rms is 0.0 and diff_mask_image is None.

    Raises:
        ValueError: If actual and expected image dimensions do not match.
    """
    if (actual.width, actual.height) != (expected.width, expected.height):
        raise ValueError(
            f"Image dimensions ({actual.width}x{actual.height}) do not match "
            f"expected dimensions ({expected.width}x{expected.height})."
        )

    act_rgb = actual.convert("RGB")
    exp_rgb = expected.convert("RGB")

    diff = ImageChops.difference(act_rgb, exp_rgb)
    stat = ImageStat.Stat(diff)
    # stat.rms provides root-mean-square value per channel [R, G, B]
    rms = math.sqrt(sum(val**2 for val in stat.rms) / len(stat.rms))

    if rms == 0.0:
        return 0.0, None

    # Generate diagnostic diff mask: dim baseline and highlight changes in neon red
    dimmed_base = Image.blend(exp_rgb, Image.new("RGB", exp_rgb.size, (0, 0, 0)), 0.65)
    diff_gray = diff.convert("L")
    mask = diff_gray.point([0] + [255] * 255)
    highlight = Image.new("RGB", exp_rgb.size, (255, 0, 100))
    diff_mask = Image.composite(highlight, dimmed_base, mask)

    return rms, diff_mask


def assert_visual_snapshot(
    actual: Image.Image,
    golden_path: Path,
    threshold: float = 0.05,
    diff_dir: Path | None = None,
) -> None:
    """Assert actual image matches golden baseline snapshot within threshold.

    Args:
        actual: Rendered image to evaluate.
        golden_path: Path to reference golden snapshot file.
        threshold: Maximum allowed RMS error threshold before failing.
        diff_dir: Optional directory where failure artifacts will be written.

    Raises:
        FileNotFoundError: If golden baseline file does not exist.
        AssertionError: If RMS difference exceeds threshold.
    """
    if not golden_path.exists():
        raise FileNotFoundError(f"Golden baseline snapshot not found: {golden_path}")

    expected = Image.open(golden_path)
    rms, diff_mask = compare_images(actual=actual, expected=expected)

    if rms > threshold:
        if diff_dir is not None:
            diff_dir.mkdir(parents=True, exist_ok=True)
            stem = golden_path.stem
            actual.save(diff_dir / f"{stem}_actual.png")
            if diff_mask is not None:
                diff_mask.save(diff_dir / f"{stem}_diff.png")

        raise AssertionError(
            f"Visual regression detected in {golden_path.name}: "
            f"RMS diff {rms:.4f} exceeds threshold {threshold:.4f}."
        )
