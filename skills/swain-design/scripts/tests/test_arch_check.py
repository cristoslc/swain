"""Tests for architecture overview diagram check."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.arch_check import has_diagram, find_architecture_overviews


class TestHasDiagram:
    """Test diagram detection in architecture overview content."""

    def test_mermaid_block(self):
        content = "# Architecture\n\n```mermaid\ngraph TD\n  A --> B\n```\n"
        assert has_diagram(content) is True

    def test_mermaid_with_spaces(self):
        content = "# Arch\n\n```  mermaid\nfoo\n```\n"
        assert has_diagram(content) is True

    def test_image_reference_markdown(self):
        content = "# Architecture\n\n![System diagram](./diagram.png)\n"
        assert has_diagram(content) is True

    def test_image_reference_html(self):
        content = '# Architecture\n\n<img src="diagram.svg" />\n'
        assert has_diagram(content) is True

    def test_diagram_heading_h2(self):
        content = "# Architecture\n\n## Diagram\n\nSee external tool.\n"
        assert has_diagram(content) is True

    def test_architecture_diagram_heading(self):
        content = "# Arch\n\n## Architecture Diagram\n\nContent.\n"
        assert has_diagram(content) is True

    def test_system_diagram_heading(self):
        content = "# Arch\n\n## System Diagram\n\nContent.\n"
        assert has_diagram(content) is True

    def test_prose_only(self):
        content = "# Architecture Overview\n\nThis system has three components.\n\nThey talk to each other.\n"
        assert has_diagram(content) is False

    def test_empty_content(self):
        assert has_diagram("") is False

    def test_code_block_not_mermaid(self):
        content = "# Arch\n\n```python\nprint('hello')\n```\n"
        assert has_diagram(content) is False

    def test_c4_diagram_heading(self):
        content = "# Arch\n\n## C4 Context Diagram\n\nContent.\n"
        assert has_diagram(content) is True


class TestFindArchitectureOverviews:
    """Test finding architecture-overview.md files in a repo."""

    def test_finds_vision_level(self, tmp_path):
        vision_dir = tmp_path / "docs" / "vision" / "Active" / "(VISION-001)-Foo"
        vision_dir.mkdir(parents=True)
        arch = vision_dir / "architecture-overview.md"
        arch.write_text("# Architecture\n\n```mermaid\ngraph TD\n```\n")

        results = find_architecture_overviews(tmp_path)
        assert len(results) == 1
        assert results[0]["path"] == str(arch.relative_to(tmp_path))
        assert results[0]["has_diagram"] is True

    def test_finds_epic_level(self, tmp_path):
        epic_dir = tmp_path / "docs" / "epic" / "Active" / "(EPIC-001)-Bar"
        epic_dir.mkdir(parents=True)
        arch = epic_dir / "architecture-overview.md"
        arch.write_text("# Architecture\n\nNo diagram here.\n")

        results = find_architecture_overviews(tmp_path)
        assert len(results) == 1
        assert results[0]["has_diagram"] is False

    def test_flags_missing_diagram(self, tmp_path):
        vision_dir = tmp_path / "docs" / "vision" / "Active" / "(VISION-001)-Foo"
        vision_dir.mkdir(parents=True)
        arch = vision_dir / "architecture-overview.md"
        arch.write_text("# Architecture\n\nJust prose.\n")

        results = find_architecture_overviews(tmp_path)
        assert len(results) == 1
        assert results[0]["has_diagram"] is False
        assert "VISION-001" in results[0]["parent_artifact"]

    def test_no_overviews(self, tmp_path):
        (tmp_path / "docs").mkdir()
        assert find_architecture_overviews(tmp_path) == []
