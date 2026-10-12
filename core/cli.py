"""Command-line interface for headless batch wallpaper and deck generation."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from core.anki import compile_anki_deck
from core.engine import render_card_pack
from core.models import TableData
from core.presets import (
    DESKTOP_2K,
    IPAD_PORTRAIT,
    LAPTOP_FHD,
    PHONE_LOCKSCREEN,
    PHONE_PANORAMA,
    DevicePreset,
)
from data.irregular_verbs import VERBS

PRESET_CHOICES: dict[str, DevicePreset] = {
    "desktop_2k": DESKTOP_2K,
    "laptop_fhd": LAPTOP_FHD,
    "ipad_portrait": IPAD_PORTRAIT,
    "phone_lockscreen": PHONE_LOCKSCREEN,
    "phone_panorama": PHONE_PANORAMA,
}


def load_dataset_from_csv(csv_path: Path) -> TableData:
    """Load and parse tabular dataset from a CSV file.

    Args:
        csv_path: Path to the source CSV file.

    Returns:
        TableData model instance containing parsed headers and rows.

    Raises:
        ValueError: If CSV file is empty.
    """
    with csv_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        records = [tuple(cell.strip() for cell in row) for row in reader if row]

    if not records:
        raise ValueError(f"CSV file is empty: {csv_path}")

    return TableData(headers=records[0], rows=tuple(records[1:]))


def build_default_table() -> TableData:
    """Build fallback default TableData from irregular verbs seed data."""
    return TableData(
        headers=("V1 (Infinitive)", "V2 (Past)", "V3 (Participle)", "Translation"),
        rows=tuple(tuple(str(cell) for cell in row) for row in VERBS),
    )


def create_parser() -> argparse.ArgumentParser:
    """Build and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="cheatsheet",
        description="Cheatsheet Engine: Headless wallpaper & Anki deck generator.",
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESET_CHOICES.keys()) + ["all"],
        default="all",
        help="Target device layout preset or 'all' for complete batch.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("screensavers"),
        help="Destination directory for generated wallpapers and decks.",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Optional path to custom CSV dataset file.",
    )
    parser.add_argument(
        "--anki",
        action="store_true",
        help="Compile matching .apkg Anki flashcard deck alongside wallpapers.",
    )
    parser.add_argument(
        "--deck-name",
        type=str,
        default="Cheatsheet Deck",
        help="Custom title for the compiled Anki deck.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console progress output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI application entrypoint returning POSIX status code.

    Args:
        argv: Optional command-line argument vector (sys.argv by default).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 0

    try:
        table = (
            load_dataset_from_csv(args.dataset)
            if args.dataset is not None
            else build_default_table()
        )
    except (ValueError, OSError) as exc:
        if not args.quiet:
            print(f"Error loading dataset: {exc}")
        return 1

    presets_to_render = (
        list(PRESET_CHOICES.values())
        if args.preset == "all"
        else [PRESET_CHOICES[args.preset]]
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for preset in presets_to_render:
        render_card_pack(
            table=table,
            preset=preset,
            output_dir=args.output_dir,
        )

    if args.anki:
        deck_slug = args.deck_name.lower().replace(" ", "_").replace("::", "_")
        apkg_path = args.output_dir / f"{deck_slug}.apkg"
        compile_anki_deck(
            table=table,
            deck_name=args.deck_name,
            output_path=apkg_path,
        )

    return 0
