"""Structured logging and layout rendering metrics observability."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

LOGGER_NAME: str = "cheatsheet"


@dataclass(frozen=True, slots=True)
class RenderReport:
    """Diagnostic report capturing layout and rendering execution metrics."""

    preset_name: str
    page_index: int
    total_pages: int
    rows_processed: int
    column_widths: tuple[int, ...]
    safe_zone_utilization: float
    duration_ms: float

    def summary(self) -> str:
        """Format a human-readable one-line diagnostic summary."""
        return (
            f"[{self.preset_name}] Page {self.page_index}/{self.total_pages} | "
            f"{self.rows_processed} rows | Widths: {self.column_widths} | "
            f"Util: {self.safe_zone_utilization:.1%} | Duration: {self.duration_ms:.2f}ms"
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize report metrics into a dictionary for reporting."""
        return {
            "preset_name": self.preset_name,
            "page_index": self.page_index,
            "total_pages": self.total_pages,
            "rows_processed": self.rows_processed,
            "column_widths": list(self.column_widths),
            "safe_zone_utilization": self.safe_zone_utilization,
            "duration_ms": self.duration_ms,
        }


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """Return a configured logger instance for cheatsheet engine operations."""
    return logging.getLogger(name)


@dataclass(slots=True)
class MetricsCollector:
    """In-memory telemetry collector capturing render execution reports."""

    _reports: list[RenderReport] = field(default_factory=list)

    def record(self, report: RenderReport) -> None:
        """Record a single render execution report."""
        self._reports.append(report)

    @property
    def reports(self) -> tuple[RenderReport, ...]:
        """Return captured render reports as an immutable tuple."""
        return tuple(self._reports)

    def clear(self) -> None:
        """Reset all captured reports."""
        self._reports.clear()
