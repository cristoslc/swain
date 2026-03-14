"""Tests for specgraph frontmatter parser."""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.parser import (
    extract_list_ids,
    extract_scalar_id,
    get_body,
    parse_artifact,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Test parse_frontmatter() against various field types."""

    def test_scalar_fields(self):
        content = '---\ntitle: "My Title"\nartifact: SPEC-001\nstatus: Proposed\n---\n# Body\n'
        fields = parse_frontmatter(content)
        assert fields is not None
        assert fields["title"] == "My Title"
        assert fields["artifact"] == "SPEC-001"
        assert fields["status"] == "Proposed"

    def test_list_fields(self):
        content = (
            "---\n"
            "artifact: SPEC-001\n"
            "depends-on-artifacts:\n"
            "  - SPIKE-012\n"
            "  - ADR-003\n"
            "linked-artifacts:\n"
            "  - EPIC-005\n"
            "---\n"
            "# Body\n"
        )
        fields = parse_frontmatter(content)
        assert fields["depends-on-artifacts"] == ["SPIKE-012", "ADR-003"]
        assert fields["linked-artifacts"] == ["EPIC-005"]

    def test_empty_list(self):
        content = "---\nartifact: SPEC-001\ndepends-on-artifacts: []\n---\n# Body\n"
        fields = parse_frontmatter(content)
        assert fields["depends-on-artifacts"] == []

    def test_empty_list_no_items(self):
        content = "---\nartifact: SPEC-001\ndepends-on-artifacts:\n---\n# Body\n"
        fields = parse_frontmatter(content)
        assert fields["depends-on-artifacts"] == []

    def test_quoted_values(self):
        content = '---\ntitle: "Quoted Title"\nartifact: SPEC-001\n---\n# Body\n'
        fields = parse_frontmatter(content)
        assert fields["title"] == "Quoted Title"

    def test_single_quoted_values(self):
        content = "---\ntitle: 'Single Quoted'\nartifact: SPEC-001\n---\n# Body\n"
        fields = parse_frontmatter(content)
        assert fields["title"] == "Single Quoted"

    def test_no_frontmatter(self):
        content = "# Just a heading\n\nSome content.\n"
        assert parse_frontmatter(content) is None

    def test_addresses_full_format(self):
        """Addresses field preserves JOURNEY-NNN.PP-NN format."""
        content = (
            "---\n"
            "artifact: SPEC-001\n"
            "addresses:\n"
            "  - JOURNEY-001.PP-03\n"
            "  - JOURNEY-002.PP-01\n"
            "---\n"
            "# Body\n"
        )
        fields = parse_frontmatter(content)
        assert fields["addresses"] == ["JOURNEY-001.PP-03", "JOURNEY-002.PP-01"]

    def test_null_tilde_values(self):
        content = "---\nartifact: SPEC-001\nparent-epic: ~\n---\n# Body\n"
        fields = parse_frontmatter(content)
        assert fields["parent-epic"] == "~"

    def test_source_issue_github_format(self):
        content = "---\nartifact: SPEC-001\nsource-issue: github:cristoslc/swain#41\n---\n# Body\n"
        fields = parse_frontmatter(content)
        assert fields["source-issue"] == "github:cristoslc/swain#41"


class TestExtractListIds:
    """Test extract_list_ids() for pulling TYPE-NNN from list fields."""

    def test_basic_list(self):
        fields = {"depends-on-artifacts": ["SPIKE-012", "ADR-003"]}
        assert extract_list_ids(fields, "depends-on-artifacts") == [
            "SPIKE-012",
            "ADR-003",
        ]

    def test_missing_field(self):
        assert extract_list_ids({}, "depends-on-artifacts") == []

    def test_empty_list(self):
        assert extract_list_ids({"depends-on-artifacts": []}, "depends-on-artifacts") == []

    def test_string_value(self):
        """If field is a string instead of list, extract IDs from it."""
        fields = {"depends-on-artifacts": "SPIKE-012"}
        assert extract_list_ids(fields, "depends-on-artifacts") == ["SPIKE-012"]

    def test_addresses_extracts_all_ids(self):
        """Addresses with PP suffixes — extract_list_ids finds all TYPE-NNN patterns."""
        fields = {"addresses": ["JOURNEY-001.PP-03"]}
        # PP-03 also matches TYPE-NNN pattern; addresses edges use full format instead
        ids = extract_list_ids(fields, "addresses")
        assert "JOURNEY-001" in ids


class TestExtractScalarId:
    """Test extract_scalar_id() for pulling TYPE-NNN from scalar fields."""

    def test_basic(self):
        assert extract_scalar_id({"parent-epic": "EPIC-005"}, "parent-epic") == "EPIC-005"

    def test_missing(self):
        assert extract_scalar_id({}, "parent-epic") is None

    def test_empty(self):
        assert extract_scalar_id({"parent-epic": ""}, "parent-epic") is None

    def test_tilde(self):
        assert extract_scalar_id({"parent-epic": "~"}, "parent-epic") is None


class TestGetBody:
    """Test body extraction after frontmatter."""

    def test_basic(self):
        content = "---\nartifact: SPEC-001\n---\n# The Body\n\nContent here.\n"
        body = get_body(content)
        assert "# The Body" in body
        assert "Content here." in body
        assert "artifact:" not in body

    def test_no_frontmatter(self):
        content = "# Just content\n"
        assert get_body(content) == content


class TestDescriptionExtraction:
    """Test description priority: question > description > body."""

    def test_question_priority(self, tmp_path):
        """Spikes use question field — it should take priority."""
        f = tmp_path / "spike.md"
        f.write_text(
            '---\nartifact: SPIKE-001\ntitle: "My Spike"\nstatus: Proposed\n'
            'question: "What is the best approach?"\n'
            'description: "A description"\n---\n# Body\n\nFirst paragraph.\n'
        )
        artifact = parse_artifact(f, tmp_path)
        assert artifact is not None
        assert artifact.description == "What is the best approach?"

    def test_description_fallback(self, tmp_path):
        f = tmp_path / "spec.md"
        f.write_text(
            '---\nartifact: SPEC-001\ntitle: "My Spec"\nstatus: Proposed\n'
            'description: "A description"\n---\n# Body\n'
        )
        artifact = parse_artifact(f, tmp_path)
        assert artifact is not None
        assert artifact.description == "A description"

    def test_body_fallback(self, tmp_path):
        f = tmp_path / "spec.md"
        f.write_text(
            '---\nartifact: SPEC-001\ntitle: "My Spec"\nstatus: Proposed\n---\n'
            "# Heading\n\nFirst body paragraph here.\n"
        )
        artifact = parse_artifact(f, tmp_path)
        assert artifact is not None
        assert artifact.description == "First body paragraph here."

    def test_title_prefix_stripped(self, tmp_path):
        f = tmp_path / "spec.md"
        f.write_text(
            '---\nartifact: SPEC-001\ntitle: "SPEC-001: My Spec"\nstatus: Proposed\n---\n# Body\n'
        )
        artifact = parse_artifact(f, tmp_path)
        assert artifact is not None
        assert artifact.title == "My Spec"

    def test_description_truncated(self, tmp_path):
        f = tmp_path / "spec.md"
        long_desc = "A" * 200
        f.write_text(
            f'---\nartifact: SPEC-001\ntitle: "Spec"\nstatus: Proposed\n'
            f"description: {long_desc}\n---\n# Body\n"
        )
        artifact = parse_artifact(f, tmp_path)
        assert artifact is not None
        assert len(artifact.description) == 120
