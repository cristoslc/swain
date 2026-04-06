"""Tests for specgraph graph builder and cache I/O."""

import multiprocessing
import json
import os
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.graph import (
    build_graph,
    build_projection,
    cache_path,
    needs_rebuild,
    read_cache,
    repo_hash,
    write_cache,
    _select_direct_parent,
)


def _concurrent_write_worker(cache_file: str, value: int) -> str:
    """Attempt one cache write from a separate process."""
    try:
        write_cache(
            {
                "nodes": {str(value): {}},
                "edges": [],
                "generated": "now",
                "repo": "/tmp/repro",
            },
            Path(cache_file),
        )
        return "ok"
    except Exception as exc:  # pragma: no cover - exercised via subprocess
        return f"{type(exc).__name__}: {exc}"


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

    def test_build_graph_fails_on_duplicate_artifact_ids(self, tmp_path):
        docs = tmp_path / "docs"
        first = docs / "spec" / "Active" / "(SPEC-001)-First"
        second = docs / "spec" / "Proposed" / "(SPEC-001)-Second"
        first.mkdir(parents=True)
        second.mkdir(parents=True)
        (first / "(SPEC-001)-First.md").write_text(
            '---\ntitle: "First"\nartifact: SPEC-001\nstatus: Active\n---\n# Spec\n',
            encoding="utf-8",
        )
        (second / "(SPEC-001)-Second.md").write_text(
            '---\ntitle: "Second"\nartifact: SPEC-001\nstatus: Proposed\n---\n# Spec\n',
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="Duplicate artifact IDs detected"):
            build_graph(tmp_path)

    def test_build_graph_ignores_materialized_symlink_paths(self, tmp_path):
        docs = tmp_path / "docs"
        parent = docs / "epic" / "Active" / "(EPIC-001)-Parent"
        child = docs / "spec" / "Proposed" / "(SPEC-001)-Child"
        parent.mkdir(parents=True)
        child.mkdir(parents=True)

        (parent / "(EPIC-001)-Parent.md").write_text(
            '---\ntitle: "Parent"\nartifact: EPIC-001\nstatus: Active\n---\n# Epic\n',
            encoding="utf-8",
        )
        (child / "(SPEC-001)-Child.md").write_text(
            '---\ntitle: "Child"\nartifact: SPEC-001\nstatus: Proposed\nparent-epic: EPIC-001\n---\n# Spec\n',
            encoding="utf-8",
        )
        (parent / child.name).symlink_to(
            os.path.relpath(child, start=parent),
            target_is_directory=True,
        )

        data = build_graph(tmp_path)

        assert sorted(data["nodes"]) == ["EPIC-001", "SPEC-001"]
        edge_tuples = {(e["from"], e["to"], e["type"]) for e in data["edges"]}
        assert ("SPEC-001", "EPIC-001", "parent-epic") in edge_tuples

    def test_projection_uses_narrowest_parent_and_folder_paths(self, tmp_path):
        docs = tmp_path / "docs"
        (docs / "vision" / "Active" / "(VISION-001)-Root").mkdir(parents=True)
        (docs / "initiative" / "Active" / "(INITIATIVE-001)-Parent").mkdir(parents=True)
        (docs / "epic" / "Active" / "(EPIC-001)-Work").mkdir(parents=True)
        (docs / "spec" / "Proposed" / "(SPEC-001)-Child").mkdir(parents=True)

        (docs / "vision" / "Active" / "(VISION-001)-Root" / "(VISION-001)-Root.md").write_text(
            '---\ntitle: "Root"\nartifact: VISION-001\nstatus: Active\ntrack: standing\n---\n# Vision\n',
            encoding="utf-8",
        )
        (docs / "initiative" / "Active" / "(INITIATIVE-001)-Parent" / "(INITIATIVE-001)-Parent.md").write_text(
            '---\ntitle: "Parent"\nartifact: INITIATIVE-001\nstatus: Active\ntrack: container\nparent-vision: VISION-001\n---\n# Initiative\n',
            encoding="utf-8",
        )
        (docs / "epic" / "Active" / "(EPIC-001)-Work" / "(EPIC-001)-Work.md").write_text(
            '---\ntitle: "Work"\nartifact: EPIC-001\nstatus: Active\ntrack: container\nparent-vision: VISION-001\nparent-initiative: INITIATIVE-001\n---\n# Epic\n',
            encoding="utf-8",
        )
        (docs / "spec" / "Proposed" / "(SPEC-001)-Child" / "(SPEC-001)-Child.md").write_text(
            '---\ntitle: "Child"\nartifact: SPEC-001\nstatus: Proposed\ntrack: implementable\nparent-initiative: INITIATIVE-001\nparent-epic: EPIC-001\n---\n# Spec\n',
            encoding="utf-8",
        )

        data = build_graph(tmp_path)
        projection = {item["artifact"]: item for item in build_projection(data["nodes"], data["edges"])}

        assert projection["VISION-001"]["placement_state"] == "root"
        assert projection["VISION-001"]["direct_parent"] is None
        assert projection["INITIATIVE-001"]["direct_parent"] == "VISION-001"
        assert projection["EPIC-001"]["direct_parent"] == "INITIATIVE-001"
        assert projection["SPEC-001"]["direct_parent"] == "EPIC-001"
        assert projection["EPIC-001"]["canonical_path"] == "docs/epic/Active/(EPIC-001)-Work"
        assert projection["SPEC-001"]["canonical_path"] == "docs/spec/Proposed/(SPEC-001)-Child"

    def test_projection_marks_unparented_when_no_direct_parent(self, tmp_path):
        docs = tmp_path / "docs"
        (docs / "spec" / "Proposed" / "(SPEC-001)-Lonely").mkdir(parents=True)
        (docs / "spec" / "Proposed" / "(SPEC-001)-Lonely" / "(SPEC-001)-Lonely.md").write_text(
            '---\ntitle: "Lonely"\nartifact: SPEC-001\nstatus: Proposed\ntrack: implementable\n---\n# Spec\n',
            encoding="utf-8",
        )

        data = build_graph(tmp_path)
        projection = build_projection(data["nodes"], data["edges"])
        assert projection == [{
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Lonely/(SPEC-001)-Lonely.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Lonely",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        }]

    def test_projection_marks_unparented_when_direct_parent_is_missing(self, tmp_path):
        docs = tmp_path / "docs"
        (docs / "spec" / "Proposed" / "(SPEC-001)-Dangling").mkdir(parents=True)
        (docs / "spec" / "Proposed" / "(SPEC-001)-Dangling" / "(SPEC-001)-Dangling.md").write_text(
            '---\ntitle: "Dangling"\nartifact: SPEC-001\nstatus: Proposed\ntrack: implementable\nparent-epic: EPIC-999\n---\n# Spec\n',
            encoding="utf-8",
        )

        data = build_graph(tmp_path)
        projection = build_projection(data["nodes"], data["edges"])
        assert projection == [{
            "artifact": "SPEC-001",
            "type": "SPEC",
            "status": "Proposed",
            "canonical_file": "docs/spec/Proposed/(SPEC-001)-Dangling/(SPEC-001)-Dangling.md",
            "canonical_path": "docs/spec/Proposed/(SPEC-001)-Dangling",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        }]

    def test_projection_converts_flat_artifact_file_to_folder_target(self, tmp_path):
        docs = tmp_path / "docs"
        (docs / "adr" / "Active").mkdir(parents=True)
        (docs / "adr" / "Active" / "(ADR-001)-Decision.md").write_text(
            '---\ntitle: "Decision"\nartifact: ADR-001\nstatus: Active\ntrack: standing\n---\n# ADR\n',
            encoding="utf-8",
        )

        data = build_graph(tmp_path)
        projection = build_projection(data["nodes"], data["edges"])

        assert projection == [{
            "artifact": "ADR-001",
            "type": "ADR",
            "status": "Active",
            "canonical_file": "docs/adr/Active/(ADR-001)-Decision.md",
            "canonical_path": "docs/adr/Active/(ADR-001)-Decision",
            "direct_parent": None,
            "placement_state": "unparented",
            "linked_artifacts": [],
            "depends_on_artifacts": [],
        }]

    def test_build_projection_includes_linked_artifacts(self):
        """Projection records include linked_artifacts from linked-artifacts edges."""
        nodes = {
            "EPIC-001": {"type": "EPIC", "status": "Active", "file": "docs/epic/Active/EPIC-001.md"},
            "DESIGN-001": {"type": "DESIGN", "status": "Active", "file": "docs/design/Active/DESIGN-001.md"},
        }
        edges = [
            {"from": "EPIC-001", "to": "DESIGN-001", "type": "linked-artifacts"},
        ]
        
        projection = build_projection(nodes, edges)
        epic_record = next(r for r in projection if r["artifact"] == "EPIC-001")
        
        assert epic_record["linked_artifacts"] == ["DESIGN-001"]

    def test_build_projection_merges_artifact_refs_into_linked(self):
        """artifact-refs edges are merged into linked_artifacts field."""
        nodes = {
            "EPIC-002": {"type": "EPIC", "status": "Active", "file": "docs/epic/Active/EPIC-002.md"},
            "DESIGN-002": {"type": "DESIGN", "status": "Active", "file": "docs/design/Active/DESIGN-002.md"},
        }
        edges = [
            {"from": "EPIC-002", "to": "DESIGN-002", "type": "artifact-refs"},
        ]
        
        projection = build_projection(nodes, edges)
        epic_record = next(r for r in projection if r["artifact"] == "EPIC-002")
        
        assert epic_record["linked_artifacts"] == ["DESIGN-002"]

    def test_build_projection_includes_depends_on_artifacts(self):
        """Projection records include depends_on_artifacts field."""
        nodes = {
            "SPEC-001": {"type": "SPEC", "status": "Proposed", "file": "docs/spec/Proposed/SPEC-001.md"},
            "SPEC-002": {"type": "SPEC", "status": "Complete", "file": "docs/spec/Complete/SPEC-002.md"},
        }
        edges = [
            {"from": "SPEC-001", "to": "SPEC-002", "type": "depends-on"},
        ]
        
        projection = build_projection(nodes, edges)
        spec_record = next(r for r in projection if r["artifact"] == "SPEC-001")
        
        assert spec_record["depends_on_artifacts"] == ["SPEC-002"]

    def test_build_projection_empty_relationships(self):
        """Artifacts with no relationships have empty lists."""
        nodes = {
            "SPEC-003": {"type": "SPEC", "status": "Proposed", "file": "docs/spec/Proposed/SPEC-003.md"},
        }
        edges = []
        
        projection = build_projection(nodes, edges)
        spec_record = next(r for r in projection if r["artifact"] == "SPEC-003")
        
        assert spec_record["linked_artifacts"] == []
        assert spec_record["depends_on_artifacts"] == []

    def test_build_projection_excludes_broken_references(self):
        """Edges to non-existent artifacts are excluded."""
        nodes = {
            "SPEC-004": {"type": "SPEC", "status": "Proposed", "file": "docs/spec/Proposed/SPEC-004.md"},
        }
        edges = [
            {"from": "SPEC-004", "to": "MISSING-001", "type": "linked-artifacts"},
            {"from": "SPEC-004", "to": "MISSING-002", "type": "depends-on"},
        ]
        
        projection = build_projection(nodes, edges)
        spec_record = next(r for r in projection if r["artifact"] == "SPEC-004")
        
        assert spec_record["linked_artifacts"] == []
        assert spec_record["depends_on_artifacts"] == []

    def test_build_projection_merges_both_linked_types(self):
        """linked-artifacts and artifact-refs both go into linked_artifacts."""
        nodes = {
            "EPIC-003": {"type": "EPIC", "status": "Active", "file": "docs/epic/Active/EPIC-003.md"},
            "DESIGN-003": {"type": "DESIGN", "status": "Active", "file": "docs/design/Active/DESIGN-003.md"},
            "ADR-003": {"type": "ADR", "status": "Active", "file": "docs/adr/Active/ADR-003.md"},
        }
        edges = [
            {"from": "EPIC-003", "to": "DESIGN-003", "type": "linked-artifacts"},
            {"from": "EPIC-003", "to": "ADR-003", "type": "artifact-refs"},
        ]
        
        projection = build_projection(nodes, edges)
        epic_record = next(r for r in projection if r["artifact"] == "EPIC-003")
        
        # Both are merged and sorted
        assert epic_record["linked_artifacts"] == ["ADR-003", "DESIGN-003"]


def test_dual_parent_spec_produces_xref_warning():
    """A spec with both parent-epic and parent-initiative produces a warning in xref."""
    import tempfile
    from pathlib import Path
    from specgraph.graph import build_graph
    with tempfile.TemporaryDirectory() as tmpdir:
        docs = os.path.join(tmpdir, "docs", "spec", "Active")
        os.makedirs(docs)
        spec_dir = os.path.join(docs, "(SPEC-099)-Dual-Parent")
        os.makedirs(spec_dir)
        with open(os.path.join(spec_dir, "(SPEC-099)-Dual-Parent.md"), "w") as f:
            f.write("---\ntitle: Dual Parent\nartifact: SPEC-099\nstatus: Active\nparent-epic: EPIC-001\nparent-initiative: INITIATIVE-001\n---\nBody.\n")
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

    def test_concurrent_writes_do_not_fail(self, tmp_path):
        """Concurrent cache rebuilds should not race on a shared temp filename."""
        cf = tmp_path / "cache.json"
        ctx = multiprocessing.get_context("fork")
        with ctx.Pool(processes=8) as pool:
            results = pool.starmap(
                _concurrent_write_worker,
                [(str(cf), i) for i in range(16)],
            )

        assert results == ["ok"] * 16
        assert read_cache(cf) is not None


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
