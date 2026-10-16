"""Unit tests for CLI parser configuration and scale factor validator."""

from __future__ import annotations

import argparse

import pytest

from core.parser import create_parser, parse_scale_factor


@pytest.mark.parametrize(
    ("raw_input", "expected"),
    [
        ("-5", 0.95),
        ("+10", 1.10),
        ("-5%", 0.95),
        ("+10%", 1.10),
        ("95%", 0.95),
        ("100%", 1.00),
        ("110%", 1.10),
        ("0.95", 0.95),
        ("1.25", 1.25),
        ("80", 0.80),
        ("120", 1.20),
    ],
)
def test_parse_scale_factor_valid(raw_input: str, expected: float) -> None:
    """Ensure valid scale percentage and multiplier inputs parse accurately."""
    assert parse_scale_factor(raw_input) == pytest.approx(expected)


@pytest.mark.parametrize("invalid_input", ["", "abc", "xyz%", "--10", "++5"])
def test_parse_scale_factor_invalid_format(invalid_input: str) -> None:
    """Ensure malformed scale strings raise ArgumentTypeError."""
    with pytest.raises(argparse.ArgumentTypeError, match="Invalid scale"):
        parse_scale_factor(invalid_input)


@pytest.mark.parametrize(
    "out_of_bounds_input",
    ["-60", "-51%", "0.4", "40%", "2.1", "250", "+110", "+101%"],
)
def test_parse_scale_factor_out_of_bounds(out_of_bounds_input: str) -> None:
    """Ensure scale factors outside [0.5, 2.0] raise ArgumentTypeError."""
    with pytest.raises(argparse.ArgumentTypeError, match="out of bounds"):
        parse_scale_factor(out_of_bounds_input)


def test_create_parser_default_scale() -> None:
    """Ensure parser assigns default scale of 1.0 when omitted."""
    parser = create_parser()
    args = parser.parse_args([])
    assert args.scale == 1.0
