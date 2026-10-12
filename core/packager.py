"""Distribution packager for bundling wallpapers and study decks."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


def calculate_file_sha256(file_path: Path) -> str:
    """Calculate SHA-256 hexadecimal digest of a filesystem file.

    Args:
        file_path: Target file path to hash.

    Returns:
        Hexadecimal hash string.
    """
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def create_bundle_pack(
    source_dir: Path,
    output_zip: Path,
    bundle_name: str,
    include_manifest: bool = True,
) -> Path:
    """Bundle directory artifacts into a zip archive with manifest.

    Args:
        source_dir: Directory containing artifacts to package.
        output_zip: Destination path for the resulting zip archive.
        bundle_name: Title of the commercial or distribution bundle.
        include_manifest: Whether to generate and embed manifest.json.

    Returns:
        Path to the created zip archive.

    Raises:
        ValueError: If source directory has no files to bundle.
    """
    files = sorted([f for f in source_dir.iterdir() if f.is_file()])
    if not files:
        raise ValueError(f"No files found to bundle in: {source_dir}")

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    checksums: dict[str, str] = {}
    for f in files:
        checksums[f.name] = calculate_file_sha256(f)

    manifest_data = {
        "bundle_name": bundle_name,
        "files": [f.name for f in files],
        "checksums": checksums,
    }

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as arc:
        for f in files:
            arc.write(f, arcname=f.name)

        if include_manifest:
            manifest_json = json.dumps(manifest_data, indent=2)
            arc.writestr("manifest.json", manifest_json)

    return output_zip
