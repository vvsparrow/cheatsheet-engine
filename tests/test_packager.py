"""Tests for batch packager and distribution bundle archiving."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from core.packager import create_bundle_pack


def test_create_bundle_pack_generates_valid_zip_with_manifest(
    tmp_path: Path,
) -> None:
    """Ensure packager zips directory files and attaches manifest with checksums."""
    source_dir = tmp_path / "artifacts"
    source_dir.mkdir()

    img_file = source_dir / "wallpaper.png"
    img_file.write_bytes(b"dummy_png_data")

    deck_file = source_dir / "deck.apkg"
    deck_file.write_bytes(b"dummy_apkg_data")

    output_zip = tmp_path / "distribution" / "mastery_pack.zip"

    result_path = create_bundle_pack(
        source_dir=source_dir,
        output_zip=output_zip,
        bundle_name="Medical Mastery Pack",
    )

    assert result_path == output_zip
    assert result_path.is_file()
    assert result_path.stat().st_size > 0

    with zipfile.ZipFile(result_path, "r") as archive:
        files = archive.namelist()
        assert "wallpaper.png" in files
        assert "deck.apkg" in files
        assert "manifest.json" in files

        manifest_data = json.loads(archive.read("manifest.json").decode("utf-8"))
        assert manifest_data["bundle_name"] == "Medical Mastery Pack"
        assert "wallpaper.png" in manifest_data["checksums"]
        assert "deck.apkg" in manifest_data["checksums"]


def test_create_bundle_pack_empty_source_raises(tmp_path: Path) -> None:
    """Ensure ValueError is raised when source directory contains no files."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    out_zip = tmp_path / "out.zip"

    with pytest.raises(ValueError, match="No files found to bundle"):
        create_bundle_pack(
            source_dir=empty_dir,
            output_zip=out_zip,
            bundle_name="Empty Pack",
        )
