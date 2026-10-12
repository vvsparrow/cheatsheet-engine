"""Pytest fixtures and configuration for cheatsheet engine test suite."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from PIL import Image

from tests.visual import assert_visual_snapshot


@pytest.fixture
def assert_snapshot() -> Callable[[Image.Image, str, float], None]:
    """Provide a fixture for asserting images against golden snapshots."""
    snapshots_dir = Path(__file__).parent / "snapshots"
    diffs_dir = snapshots_dir / "diffs"

    def _assert(
        actual: Image.Image,
        snapshot_name: str,
        threshold: float = 0.05,
    ) -> None:
        golden_path = snapshots_dir / snapshot_name
        assert_visual_snapshot(
            actual=actual,
            golden_path=golden_path,
            threshold=threshold,
            diff_dir=diffs_dir,
        )

    return _assert
