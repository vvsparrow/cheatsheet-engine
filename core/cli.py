"""Command-line interface for headless batch wallpaper and deck generation."""

from __future__ import annotations

import time
from dataclasses import replace
from pathlib import Path

from PIL import Image

from core.anki import compile_anki_deck
from core.loader import build_default_table, load_dataset_from_csv
from core.models import TableData
from core.overlays import apply_device_overlay
from core.packager import create_bundle_pack
from core.parser import PRESET_CHOICES, create_parser
from core.presets import DevicePreset
from core.series import render_card_pack
from core.theme import Theme, get_theme


def _render_presets_and_mockups(
    table: TableData,
    presets: list[DevicePreset],
    output_dir: Path,
    mockups: bool = False,
    theme: Theme | None = None,
) -> None:
    """Render wallpapers for presets and optionally generate device mockups."""
    active_theme = theme or get_theme("dark")
    for preset in presets:
        card_paths = render_card_pack(
            table=table,
            preset=preset,
            output_dir=output_dir,
            theme=active_theme,
        )
        if mockups and preset.has_mockup:
            for card_path in card_paths:
                with Image.open(card_path) as img:
                    mockup = apply_device_overlay(image=img, preset=preset)
                    mockup.save(card_path.with_name(f"{card_path.stem}_mockup.png"))


def main(
    argv: list[str] | None = None,
    max_watch_cycles: int | None = None,
) -> int:
    """CLI application entrypoint returning POSIX status code.

    Args:
        argv: Optional command-line argument vector (sys.argv by default).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    try:
        args = parser.parse_args(argv)
        if args.watch and args.dataset is None:
            if not args.quiet:
                print("Error: --watch requires --dataset to be specified.")
            return 1
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
    if args.scale != 1.0:
        presets_to_render = [
            replace(
                p,
                font_size=max(8, round(p.font_size * args.scale)),
                row_height=max(12, round(p.row_height * args.scale)),
                min_font_size=max(6, round(p.min_font_size * args.scale)),
            )
            for p in presets_to_render
        ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    theme = get_theme(args.theme)

    _render_presets_and_mockups(
        table=table,
        presets=presets_to_render,
        output_dir=args.output_dir,
        mockups=args.mockups,
        theme=theme,
    )

    if args.anki:
        deck_slug = args.deck_name.lower().replace(" ", "_").replace("::", "_")
        apkg_path = args.output_dir / f"{deck_slug}.apkg"
        compile_anki_deck(
            table=table,
            deck_name=args.deck_name,
            output_path=apkg_path,
        )

    if args.bundle:
        bundle_slug = args.bundle_name.lower().replace(" ", "_").replace("::", "_")
        zip_path = args.output_dir / f"{bundle_slug}.zip"
        create_bundle_pack(
            source_dir=args.output_dir,
            output_zip=zip_path,
            bundle_name=args.bundle_name,
        )

    if args.watch and args.dataset is not None:
        last_mtime = args.dataset.stat().st_mtime
        cycles = 0
        try:
            while True:
                if max_watch_cycles is not None and cycles >= max_watch_cycles:
                    break
                time.sleep(0.05)
                current_mtime = args.dataset.stat().st_mtime
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    table = load_dataset_from_csv(args.dataset)
                    _render_presets_and_mockups(
                        table=table,
                        presets=presets_to_render,
                        output_dir=args.output_dir,
                        mockups=args.mockups,
                        theme=theme,
                    )
                    if not args.quiet:
                        print(f"[WATCH] Re-rendered at {time.strftime('%H:%M:%S')}")
                cycles += 1
        except KeyboardInterrupt:
            if not args.quiet:
                print("\n[WATCH] Stopped.")
            return 0

    return 0
