"""Tests for headless CLI entrypoint and batch wallpaper generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.cli import main


def test_cli_help_flag_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """Ensure --help displays usage information and exits with code 0."""
    exit_code = main(["--help"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage:" in captured.out.lower()
    assert "--preset" in captured.out


def test_cli_renders_single_preset(tmp_path: Path) -> None:
    """Ensure CLI renders designated preset wallpaper and exits with 0."""
    out_dir = tmp_path / "wallpapers"
    exit_code = main(["--preset", "laptop_fhd", "--output-dir", str(out_dir)])
    assert exit_code == 0

    generated_files = list(out_dir.glob("*.png"))
    assert len(generated_files) > 0


def test_cli_renders_preset_with_anki_deck(tmp_path: Path) -> None:
    """Ensure --anki flag compiles matching .apkg deck alongside wallpapers."""
    out_dir = tmp_path / "bundle"
    exit_code = main(
        ["--preset", "phone_lockscreen", "--output-dir", str(out_dir), "--anki"]
    )
    assert exit_code == 0

    apkg_files = list(out_dir.glob("*.apkg"))
    assert len(apkg_files) == 1
    assert apkg_files[0].stat().st_size > 0


def test_cli_invalid_preset_returns_error_code(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure invalid preset name fails validation with non-zero exit code."""
    exit_code = main(["--preset", "invalid_device"])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err.lower()


def test_cli_renders_with_custom_csv_dataset(tmp_path: Path) -> None:
    """Ensure CLI correctly ingests and renders custom CSV dataset file."""
    csv_file = tmp_path / "custom_data.csv"
    csv_file.write_text("Lab_Test,Normal_Range\nCRP,<5 mg/L\n", encoding="utf-8")

    out_dir = tmp_path / "custom_out"
    exit_code = main(
        [
            "--dataset",
            str(csv_file),
            "--preset",
            "laptop_fhd",
            "--output-dir",
            str(out_dir),
        ]
    )
    assert exit_code == 0
    assert len(list(out_dir.glob("*.png"))) > 0


def test_cli_empty_csv_dataset_returns_exit_code_one(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure empty CSV dataset triggers clean exit code 1 with error message."""
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("", encoding="utf-8")

    exit_code = main(["--dataset", str(empty_csv)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "error loading dataset" in captured.out.lower()


def test_cli_watch_without_dataset_fails(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure --watch without --dataset fails with error code 1."""
    exit_code = main(["--watch"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "--watch requires --dataset" in captured.out.lower()


def test_cli_watch_mode_renders_and_cycles_cleanly(tmp_path: Path) -> None:
    """Ensure --watch executes render cycle and terminates gracefully."""
    csv_file = tmp_path / "watch_data.csv"
    csv_file.write_text("Lab_Test,Normal_Range\nK+,3.5-5.0\n", encoding="utf-8")
    out_dir = tmp_path / "watch_out"

    exit_code = main(
        [
            "--dataset",
            str(csv_file),
            "--preset",
            "laptop_fhd",
            "--output-dir",
            str(out_dir),
            "--watch",
        ],
        max_watch_cycles=1,
    )

    assert exit_code == 0
    assert len(list(out_dir.glob("*.png"))) > 0
