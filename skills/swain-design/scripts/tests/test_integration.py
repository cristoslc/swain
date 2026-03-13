"""Integration test: verify Python specgraph build matches bash specgraph build."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts dir to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from specgraph.graph import build_graph, cache_path


def _get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def _normalize_graph(data: dict) -> dict:
    """Normalize a graph for comparison: sort edges, remove timestamps."""
    normalized = dict(data)
    normalized.pop("generated", None)
    # Sort edges by (from, to, type) for stable comparison
    normalized["edges"] = sorted(
        normalized["edges"], key=lambda e: (e["from"], e["to"], e["type"])
    )
    # Sort nodes by key
    normalized["nodes"] = dict(sorted(normalized["nodes"].items()))
    return normalized


@pytest.fixture
def repo_root():
    return _get_repo_root()


class TestBuildParity:
    """Verify Python build produces identical output to bash build."""

    def test_python_build_produces_valid_cache(self, repo_root):
        """Python build creates a cache with nodes, edges, generated, and repo keys."""
        data = build_graph(repo_root)
        assert "nodes" in data
        assert "edges" in data
        assert "generated" in data
        assert "repo" in data
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0

    def test_python_matches_bash_node_count(self, repo_root):
        """Python build finds the same number of artifacts as bash."""
        # Run bash build
        specgraph_sh = repo_root / "skills" / "swain-design" / "scripts" / "specgraph.sh"
        subprocess.run(
            ["bash", str(specgraph_sh), "build"],
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        bash_cache = cache_path(str(repo_root))
        with open(bash_cache) as f:
            bash_data = json.load(f)

        py_data = build_graph(repo_root)

        assert len(py_data["nodes"]) == len(bash_data["nodes"]), (
            f"Node count mismatch: Python={len(py_data['nodes'])}, "
            f"Bash={len(bash_data['nodes'])}"
        )

    def test_python_matches_bash_edge_count(self, repo_root):
        """Python build finds the same number of edges as bash."""
        specgraph_sh = repo_root / "skills" / "swain-design" / "scripts" / "specgraph.sh"
        subprocess.run(
            ["bash", str(specgraph_sh), "build"],
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        bash_cache = cache_path(str(repo_root))
        with open(bash_cache) as f:
            bash_data = json.load(f)

        py_data = build_graph(repo_root)

        assert len(py_data["edges"]) == len(bash_data["edges"]), (
            f"Edge count mismatch: Python={len(py_data['edges'])}, "
            f"Bash={len(bash_data['edges'])}"
        )

    def test_python_matches_bash_node_ids(self, repo_root):
        """Python build finds the exact same artifact IDs as bash."""
        specgraph_sh = repo_root / "skills" / "swain-design" / "scripts" / "specgraph.sh"
        subprocess.run(
            ["bash", str(specgraph_sh), "build"],
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        bash_cache = cache_path(str(repo_root))
        with open(bash_cache) as f:
            bash_data = json.load(f)

        py_data = build_graph(repo_root)

        bash_ids = set(bash_data["nodes"].keys())
        py_ids = set(py_data["nodes"].keys())

        missing_in_py = bash_ids - py_ids
        extra_in_py = py_ids - bash_ids

        assert not missing_in_py, f"Python missing: {missing_in_py}"
        assert not extra_in_py, f"Python has extra: {extra_in_py}"

    def test_python_matches_bash_edges(self, repo_root):
        """Python build produces the exact same edges as bash (normalized)."""
        specgraph_sh = repo_root / "skills" / "swain-design" / "scripts" / "specgraph.sh"
        subprocess.run(
            ["bash", str(specgraph_sh), "build"],
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        bash_cache = cache_path(str(repo_root))
        with open(bash_cache) as f:
            bash_data = json.load(f)

        py_data = build_graph(repo_root)

        bash_norm = _normalize_graph(bash_data)
        py_norm = _normalize_graph(py_data)

        assert py_norm["edges"] == bash_norm["edges"], (
            "Edge mismatch. Differences:\n"
            + _edge_diff(bash_norm["edges"], py_norm["edges"])
        )

    def test_python_matches_bash_node_metadata(self, repo_root):
        """Python nodes have matching title, status, type, and file fields."""
        specgraph_sh = repo_root / "skills" / "swain-design" / "scripts" / "specgraph.sh"
        subprocess.run(
            ["bash", str(specgraph_sh), "build"],
            capture_output=True,
            check=True,
            cwd=repo_root,
        )
        bash_cache = cache_path(str(repo_root))
        with open(bash_cache) as f:
            bash_data = json.load(f)

        py_data = build_graph(repo_root)

        for aid in bash_data["nodes"]:
            if aid not in py_data["nodes"]:
                continue
            bash_node = bash_data["nodes"][aid]
            py_node = py_data["nodes"][aid]

            for field in ("title", "status", "type", "file"):
                assert py_node[field] == bash_node[field], (
                    f"{aid}.{field}: Python={py_node[field]!r}, "
                    f"Bash={bash_node[field]!r}"
                )


def _edge_diff(bash_edges: list, py_edges: list) -> str:
    """Produce a human-readable diff of edge lists."""
    bash_set = {(e["from"], e["to"], e["type"]) for e in bash_edges}
    py_set = {(e["from"], e["to"], e["type"]) for e in py_edges}

    lines = []
    for e in sorted(bash_set - py_set):
        lines.append(f"  BASH only: {e[0]} -> {e[1]} ({e[2]})")
    for e in sorted(py_set - bash_set):
        lines.append(f"  PY only:   {e[0]} -> {e[1]} ({e[2]})")
    return "\n".join(lines) if lines else "(no diff)"
