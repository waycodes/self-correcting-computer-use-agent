"""Smoke tests to verify basic package functionality."""

from sca import __version__
from sca.cli import main


def test_version_exists() -> None:
    """Package version is defined."""
    assert __version__ == "0.1.0"


def test_cli_help_returns_zero() -> None:
    """CLI --help returns exit code 0."""
    import sys
    from unittest.mock import patch

    with patch.object(sys, "argv", ["sca", "--help"]):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0
