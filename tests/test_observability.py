"""Tests for structured logging and layout rendering metrics."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from core.engine import render_wallpaper
from core.models import TableData
from core.observability import MetricsCollector, RenderReport, get_logger
from core.presets import LAPTOP_FHD


def test_render_report_instantiation_and_immutability() -> None:
    """Ensure RenderReport instantiates with valid metrics and is immutable."""
    report = RenderReport(
        preset_name="laptop_fhd",
        page_index=1,
        total_pages=3,
        rows_processed=42,
        column_widths=(120, 180, 240),
        safe_zone_utilization=0.785,
        duration_ms=14.2,
    )

    assert report.preset_name == "laptop_fhd"
    assert report.page_index == 1
    assert report.total_pages == 3
    assert report.rows_processed == 42
    assert report.column_widths == (120, 180, 240)
    assert report.safe_zone_utilization == 0.785
    assert report.duration_ms == 14.2

    with pytest.raises(AttributeError):
        report.rows_processed = 50  # type: ignore[misc]


def test_get_logger_captures_levels_cleanly(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ensure get_logger produces named logger capturing DEBUG, INFO, and ERROR."""
    logger = get_logger("cheatsheet.test")

    with caplog.at_level(logging.DEBUG):
        logger.debug("Debug event: resolving font metrics")
        logger.info("Info event: rendered wallpaper page 1")
        logger.error("Error event: boundary clipping detected")

    records = [r for r in caplog.records if r.name == "cheatsheet.test"]
    assert len(records) == 3

    assert records[0].levelno == logging.DEBUG
    assert "resolving font metrics" in records[0].message

    assert records[1].levelno == logging.INFO
    assert "rendered wallpaper page 1" in records[1].message

    assert records[2].levelno == logging.ERROR
    assert "boundary clipping detected" in records[2].message


def test_render_report_summary_and_dict() -> None:
    """Ensure RenderReport formats summary string and serializes to dict."""
    report = RenderReport(
        preset_name="laptop_fhd",
        page_index=1,
        total_pages=2,
        rows_processed=30,
        column_widths=(100, 200),
        safe_zone_utilization=0.65,
        duration_ms=12.5,
    )

    summary = report.summary()
    assert "[laptop_fhd]" in summary
    assert "Page 1/2" in summary
    assert "30 rows" in summary
    assert "12.50ms" in summary

    data = report.to_dict()
    assert data["preset_name"] == "laptop_fhd"
    assert data["rows_processed"] == 30
    assert data["column_widths"] == [100, 200]
    assert data["safe_zone_utilization"] == 0.65


def test_metrics_collector_records_and_clears() -> None:
    """Ensure MetricsCollector stores reports and supports clearing state."""
    collector = MetricsCollector()
    assert len(collector.reports) == 0

    report1 = RenderReport("fhd", 1, 1, 10, (50,), 0.5, 5.0)
    report2 = RenderReport("2k", 1, 1, 20, (80,), 0.7, 8.0)

    collector.record(report1)
    collector.record(report2)

    assert len(collector.reports) == 2
    assert collector.reports[0].preset_name == "fhd"
    assert collector.reports[1].preset_name == "2k"

    collector.clear()
    assert len(collector.reports) == 0


def test_render_wallpaper_records_metrics_and_logs(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ensure render_wallpaper records metrics into collector and logs summary."""
    collector = MetricsCollector()
    output_file = tmp_path / "test_wallpaper.png"

    table = TableData(
        headers=("V1", "V2", "V3"),
        rows=(
            ("go", "went", "gone"),
            ("take", "took", "taken"),
        ),
    )

    with caplog.at_level(logging.INFO):
        render_wallpaper(
            table=table,
            preset=LAPTOP_FHD,
            output_path=output_file,
            collector=collector,
        )

    assert len(collector.reports) == 1
    report = collector.reports[0]
    assert report.preset_name == LAPTOP_FHD.name
    assert report.rows_processed == 2
    assert report.duration_ms > 0.0
    assert 0.0 < report.safe_zone_utilization <= 1.0
    assert len(report.column_widths) == 3

    log_records = [r for r in caplog.records if r.name == "cheatsheet"]
    assert any("Laptop Full HD" in r.message for r in log_records)
