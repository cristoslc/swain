"""Tests for specgraph OSC 8 link helper utilities."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.links import art_link, file_link, is_tty


class TestIsTty:
    """Test is_tty() TTY detection."""

    def test_returns_false_when_not_a_tty(self):
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            assert is_tty() is False

    def test_returns_true_when_is_a_tty(self):
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            assert is_tty() is True


class TestArtLink:
    """Test art_link() OSC 8 hyperlink generation."""

    def test_non_tty_returns_artifact_id_only(self):
        """When stdout is not a TTY, art_link returns just the artifact_id."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = art_link("SPEC-001", "docs/spec/SPEC-001.md", "/repo/root")
        assert result == "SPEC-001"
        assert "\x1b" not in result

    def test_tty_returns_osc8_sequence(self):
        """When stdout is a TTY, art_link returns an OSC 8 escape sequence."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = art_link("SPEC-001", "docs/spec/SPEC-001.md", "/repo/root")
        assert "\x1b]8;;" in result

    def test_tty_url_contains_filepath(self):
        """The OSC 8 URL contains the file path."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = art_link("SPEC-001", "docs/spec/SPEC-001.md", "/repo/root")
        assert "docs/spec/SPEC-001.md" in result

    def test_tty_url_contains_repo_root(self):
        """The OSC 8 URL contains the repo root."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = art_link("SPEC-001", "docs/spec/SPEC-001.md", "/repo/root")
        assert "/repo/root" in result

    def test_tty_text_is_artifact_id(self):
        """The visible text in the OSC 8 sequence is the artifact_id."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = art_link("SPEC-001", "docs/spec/SPEC-001.md", "/repo/root")
        # OSC 8 format: \x1b]8;;URL\x1b\\TEXT\x1b]8;;\x1b\\
        # Text appears after the first \x1b\\ and before the closing \x1b]8;;
        assert "SPEC-001" in result

    def test_tty_osc8_closing_sequence(self):
        """The OSC 8 sequence is properly closed."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = art_link("SPEC-001", "docs/spec/SPEC-001.md", "/repo/root")
        # Closing sequence: \x1b]8;;\x1b\\
        assert result.endswith("\x1b]8;;\x1b\\")

    def test_non_tty_empty_filepath_returns_artifact_id(self):
        """When filepath is empty and not a TTY, just return artifact_id."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = art_link("EPIC-003", "", "/repo/root")
        assert result == "EPIC-003"

    def test_tty_empty_filepath_returns_artifact_id_only(self):
        """When filepath is empty even with a TTY, return just the artifact_id."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = art_link("EPIC-003", "", "/repo/root")
        assert result == "EPIC-003"

    def test_tty_full_osc8_format(self):
        """Verify the exact OSC 8 format: \\x1b]8;;URL\\x1b\\TEXT\\x1b]8;;\\x1b\\"""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = art_link("ADR-001", "docs/adr/ADR-001.md", "/my/repo")
        expected_url = "file:///my/repo/docs/adr/ADR-001.md"
        expected = f"\x1b]8;;{expected_url}\x1b\\ADR-001\x1b]8;;\x1b\\"
        assert result == expected


class TestFileLink:
    """Test file_link() OSC 8 hyperlink generation with custom text."""

    def test_non_tty_returns_text_only(self):
        """When stdout is not a TTY, file_link returns just the text."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = file_link("View file", "docs/spec/SPEC-001.md", "/repo/root")
        assert result == "View file"
        assert "\x1b" not in result

    def test_tty_returns_osc8_sequence(self):
        """When stdout is a TTY, file_link returns an OSC 8 escape sequence."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = file_link("View file", "docs/spec/SPEC-001.md", "/repo/root")
        assert "\x1b]8;;" in result

    def test_tty_url_contains_filepath(self):
        """The OSC 8 URL contains the file path."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = file_link("View file", "docs/spec/SPEC-001.md", "/repo/root")
        assert "docs/spec/SPEC-001.md" in result

    def test_tty_text_is_display_text(self):
        """The visible text in the OSC 8 sequence is the provided text."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = file_link("Custom Label", "docs/spec/SPEC-001.md", "/repo/root")
        assert "Custom Label" in result

    def test_tty_full_osc8_format(self):
        """Verify the exact OSC 8 format for file_link."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = file_link("My Label", "docs/adr/ADR-001.md", "/my/repo")
        expected_url = "file:///my/repo/docs/adr/ADR-001.md"
        expected = f"\x1b]8;;{expected_url}\x1b\\My Label\x1b]8;;\x1b\\"
        assert result == expected

    def test_non_tty_empty_filepath_returns_text(self):
        """When filepath is empty and not a TTY, return just the text."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            result = file_link("My Label", "", "/repo/root")
        assert result == "My Label"

    def test_tty_empty_filepath_returns_text_only(self):
        """When filepath is empty even with a TTY, return just the text (no link)."""
        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = True
            result = file_link("My Label", "", "/repo/root")
        assert result == "My Label"
        assert "\x1b" not in result
