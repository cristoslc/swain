"""Tests for specgraph graph builder and cache I/O."""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.graph import (
    build_graph,
    cache_path,
    needs_rebuild,
    read_cache,
    repo_hash,
    write_cache,
)


class TestRepoHash:
    """Test cache path derivation matches bash."""

    def test_hash_deterministic(self):
        h = repo_hash("/Users/cristos/Documents/code/swain")
        assert len(h) == 12
        assert h == repo_hash("/Users/cristos/Documents/code/swain")

    def test_different_paths_different_hashes(self):
        assert repo_hash("/foo") != repo_hash("/bar")

    def test_cache_path_format(self):
        cp = cache_path("/Users/cristos/Documents/code/swain")
        assert cp.name.startswith("agents-specgraph-")
        assert cp.name.endswith(".json")
        assert cp.parent == Path("/tmp")


class TestBuildGraph:
    """Test graph building from fixture files."""

    def test_basic_two_artifacts(self, tmp_path):
        """Two artifacts with a depends-on edge."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "epic.md").write_text(
            '---\ntitle: "My Epic"\nartifact: EPIC-001\nstatus: Active\n---\n# Epic\n'
        )
        (docs / "spec.md").write_text(
            '---\ntitle: "My Spec"\nartifact: SPEC-001\nstatus: Proposed\n'
            "parent-epic: EPIC-001\n"
            "depends-on-artifacts:\n  - EPIC-001\n---\n# Spec\n"
        )

        data = build_graph(tmp_path)

        assert "EPIC-001" in data["nodes"]
        assert "SPEC-001" in data["nodes"]
        assert data["nodes"]["EPIC-001"]["type"] == "EPIC"
        assert data["nodes"]["SPEC-001"]["type"] == "SPEC"

        # Check edges
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("SPEC-001", "EPIC-001", "depends-on") in edge_tuples
        assert ("SPEC-001", "EPIC-001", "parent-epic") in edge_tuples

    def test_linked_artifacts_edge(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "adr.md").write_text(
            '---\ntitle: "ADR"\nartifact: ADR-001\nstatus: Active\n'
            "linked-artifacts:\n  - SPEC-001\n---\n# ADR\n"
        )
        (docs / "spec.md").write_text(
            '---\ntitle: "Spec"\nartifact: SPEC-001\nstatus: Proposed\n---\n# Spec\n'
        )

        data = build_graph(tmp_path)
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("ADR-001", "SPEC-001", "linked-artifacts") in edge_tuples

    def test_validates_edge(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "runbook.md").write_text(
            '---\ntitle: "Runbook"\nartifact: RUNBOOK-001\nstatus: Active\n'
            "validates:\n  - SPEC-001\n---\n# Runbook\n"
        )
        (docs / "spec.md").write_text(
            '---\ntitle: "Spec"\nartifact: SPEC-001\nstatus: Proposed\n---\n# Spec\n'
        )

        data = build_graph(tmp_path)
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("RUNBOOK-001", "SPEC-001", "validates") in edge_tuples

    def test_addresses_preserves_full_format(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "spec.md").write_text(
            '---\ntitle: "Spec"\nartifact: SPEC-001\nstatus: Proposed\n'
            "addresses:\n  - JOURNEY-001.PP-03\n---\n# Spec\n"
        )

        data = build_graph(tmp_path)
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("SPEC-001", "JOURNEY-001.PP-03", "addresses") in edge_tuples

    def test_source_issue_edge(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "spec.md").write_text(
            '---\ntitle: "Spec"\nartifact: SPEC-001\nstatus: Proposed\n'
            "source-issue: github:org/repo#42\n---\n# Spec\n"
        )

        data = build_graph(tmp_path)
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("SPEC-001", "github:org/repo#42", "source-issue") in edge_tuples

    def test_superseded_by_edge(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "adr1.md").write_text(
            '---\ntitle: "Old ADR"\nartifact: ADR-001\nstatus: Superseded\n'
            "superseded-by: ADR-002\n---\n# Old\n"
        )
        (docs / "adr2.md").write_text(
            '---\ntitle: "New ADR"\nartifact: ADR-002\nstatus: Active\n---\n# New\n'
        )

        data = build_graph(tmp_path)
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("ADR-001", "ADR-002", "superseded-by") in edge_tuples

    def test_parent_vision_edge(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "vision.md").write_text(
            '---\ntitle: "Vision"\nartifact: VISION-001\nstatus: Active\n---\n# Vision\n'
        )
        (docs / "epic.md").write_text(
            '---\ntitle: "Epic"\nartifact: EPIC-001\nstatus: Active\n'
            "parent-vision: VISION-001\n---\n# Epic\n"
        )

        data = build_graph(tmp_path)
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("EPIC-001", "VISION-001", "parent-vision") in edge_tuples

    def test_skips_non_artifact_files(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "README.md").write_text("# README\n\nNot an artifact.\n")
        (docs / "list-spec.md").write_text("# Spec Index\n")
        (docs / "real.md").write_text(
            '---\ntitle: "Real"\nartifact: SPEC-001\nstatus: Proposed\n---\n# Real\n'
        )

        data = build_graph(tmp_path)
        assert len(data["nodes"]) == 1
        assert "SPEC-001" in data["nodes"]

    def test_parent_initiative_edge(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "initiative.md").write_text(
            '---\ntitle: "Initiative"\nartifact: INITIATIVE-001\nstatus: Active\n---\n# Initiative\n'
        )
        (docs / "epic.md").write_text(
            '---\ntitle: "Epic"\nartifact: EPIC-001\nstatus: Active\n'
            "parent-initiative: INITIATIVE-001\n---\n# Epic\n"
        )

        data = build_graph(tmp_path)
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("EPIC-001", "INITIATIVE-001", "parent-initiative") in edge_tuples

    def test_skips_empty_refs(self, tmp_path):
        """Empty, null, tilde values should not create edges."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "spec.md").write_text(
            '---\ntitle: "Spec"\nartifact: SPEC-001\nstatus: Proposed\n'
            "parent-epic: ~\nsuperseded-by:\nevidence-pool:\n---\n# Spec\n"
        )

        data = build_graph(tmp_path)
        assert len(data["edges"]) == 0

    def test_priority_weight_extraction(self, tmp_path):
        """Vision artifact with priority-weight in frontmatter should be in node dict."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "vision.md").write_text(
            '---\ntitle: "My Vision"\nartifact: VISION-001\nstatus: Active\n'
            "priority-weight: high\n---\n# Vision\n"
        )

        data = build_graph(tmp_path)
        assert "VISION-001" in data["nodes"]
        assert data["nodes"]["VISION-001"]["priority_weight"] == "high"


def test_dual_parent_spec_produces_xref_warning():
    """A spec with both parent-epic and parent-initiative produces a warning in xref."""
    import tempfile, os
    from pathlib import Path
    from specgraph.graph import build_graph
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = os.path.join(tmpdir, "docs", "spec", "Ready")
        os.makedirs(docs)
        spec_dir = os.path.join(docs, "(SPEC-099)-Dual-Parent")
        os.makedirs(spec_dir)
        with open(os.path.join(spec_dir, "(SPEC-099)-Dual-Parent.md"), "w") as f:
            f.write("---\ntitle: Dual Parent\nartifact: SPEC-099\nstatus: Ready\nparent-epic: EPIC-001\nparent-initiative: INITIATIVE-001\n---\nBody.\n")
        result = build_graph(Path(tmpdir))
        # Check for dual-parent warning in xref
        warnings = [x for x in result.get("xref", []) if x.get("artifact") == "SPEC-099"]
        assert any(w.get("dual_parent") for w in warnings), f"Expected dual_parent warning, got: {warnings}"


class TestCacheIO:
    """Test cache read/write operations."""

    def test_write_and_read(self, tmp_path):
        cf = tmp_path / "cache.json"
        data = {"nodes": {"A": {}}, "edges": [], "generated": "now", "repo": "/foo"}
        write_cache(data, cf)
        loaded = read_cache(cf)
        assert loaded == data

    def test_read_missing(self, tmp_path):
        cf = tmp_path / "nonexistent.json"
        assert read_cache(cf) is None

    def test_atomic_write(self, tmp_path):
        """Write should be atomic (no .tmp file left behind)."""
        cf = tmp_path / "cache.json"
        write_cache({"test": True}, cf)
        assert cf.exists()
        assert not cf.with_suffix(".tmp").exists()


class TestNeedsRebuild:
    """Test cache staleness detection."""

    def test_no_cache_needs_rebuild(self, tmp_path):
        cf = tmp_path / "cache.json"
        docs = tmp_path / "docs"
        docs.mkdir()
        assert needs_rebuild(cf, docs) is True

    def test_fresh_cache(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "spec.md").write_text("# old\n")

        import time
        time.sleep(0.05)

        cf = tmp_path / "cache.json"
        cf.write_text("{}")

        assert needs_rebuild(cf, docs) is False

    def test_stale_cache(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()

        cf = tmp_path / "cache.json"
        cf.write_text("{}")

        import time
        time.sleep(0.05)

        (docs / "spec.md").write_text("# new\n")

        assert needs_rebuild(cf, docs) is True
