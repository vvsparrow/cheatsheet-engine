"""Multi-page card series generation and pagination pipeline."""

from __future__ import annotations

from pathlib import Path

from core.engine import render_wallpaper
from core.layout import calculate_page_layout
from core.models import TableData
from core.observability import MetricsCollector
from core.presets import DevicePreset
from core.theme import DARK_THEME, Theme

__all__ = ["render_card_pack"]


def _plan_pages(table: TableData, preset: DevicePreset) -> tuple[int, ...]:
    """Plan cursor offsets for every page of the dataset.

    Args:
        table: Tabular dataset to paginate.
        preset: Target device layout and resolution preset.

    Returns:
        Tuple of zero-based start indices, one per page, in render order.
    """
    if table.row_count == 0:
        return (0,)

    offsets: list[int] = []
    cursor = 0
    while cursor < table.row_count:
        offsets.append(cursor)
        layout = calculate_page_layout(table=table, preset=preset, start_idx=cursor)
        if not layout.page_rows:
            break
        cursor += len(layout.page_rows)

    return tuple(offsets) if offsets else (0,)


def render_card_pack(
    table: TableData,
    preset: DevicePreset,
    output_dir: Path,
    collector: MetricsCollector | None = None,
    theme: Theme = DARK_THEME,
) -> tuple[Path, ...]:
    """Render complete paginated series of wallpapers for the dataset.

    Args:
        table: Tabular dataset to render across multiple pages.
        preset: Target device layout and resolution preset.
        output_dir: Destination directory for the generated card series.
        collector: Optional metrics collector to capture execution report.
        theme: Color palette and visual tokens used for rendering.

    Returns:
        Tuple of filesystem Paths to the generated images in order.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = preset.name.lower().replace(" ", "_")

    if table.row_count == 0:
        single_path = output_dir / f"{slug}_part_1_of_1.png"
        render_wallpaper(
            table=table,
            preset=preset,
            output_path=single_path,
            start_idx=0,
            page_index=1,
            total_pages=1,
            collector=collector,
            theme=theme,
        )
        return (single_path,)

    offsets = _plan_pages(table=table, preset=preset)
    total_pages = len(offsets)
    paths: list[Path] = []

    for page_index, start_idx in enumerate(offsets, start=1):
        card_name = f"{slug}_part_{page_index}_of_{total_pages}.png"
        card_path = output_dir / card_name
        render_wallpaper(
            table=table,
            preset=preset,
            output_path=card_path,
            start_idx=start_idx,
            page_index=page_index,
            total_pages=total_pages,
            collector=collector,
            theme=theme,
        )
        paths.append(card_path)

    return tuple(paths)
