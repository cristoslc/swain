"""Regression tests for symlinked chart entrypoints."""

from __future__ import annotations

import subprocess
import json
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS_DIR.parent.parent.parent


def test_symlinked_chart_wrapper_ignores_sibling_specgraph_shim(tmp_path):
    """A symlinked chart.sh should resolve imports from the real scripts dir."""
    bin_dir = tmp_path / ".agents" / "bin"
    bin_dir.mkdir(parents=True)

    (bin_dir / "chart.sh").symlink_to(SCRIPTS_DIR / "chart.sh")
    (bin_dir / "chart_cli.py").symlink_to(SCRIPTS_DIR / "chart_cli.py")
    (bin_dir / "specgraph.py").write_text(
        "from specgraph.cli import main\n"
        "if __name__ == '__main__':\n"
        "    main()\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(bin_dir / "chart.sh"), "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Vision-rooted hierarchy display" in result.stdout


def test_chart_projection_outputs_machine_readable_records(tmp_path):
    """The symlinked wrapper should expose the projection command."""
    repo_root = tmp_path / "repo"
    docs = repo_root / "docs" / "vision" / "Active" / "(VISION-001)-Root"
    docs.mkdir(parents=True)
    (docs / "(VISION-001)-Root.md").write_text(
        '---\ntitle: "Root"\nartifact: VISION-001\nstatus: Active\ntrack: standing\n---\n# Vision\n',
        encoding="utf-8",
    )

    bin_dir = repo_root / ".agents" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "chart.sh").symlink_to(SCRIPTS_DIR / "chart.sh")
    (bin_dir / "chart_cli.py").symlink_to(SCRIPTS_DIR / "chart_cli.py")

    result = subprocess.run(
        ["bash", str(bin_dir / "chart.sh"), "projection", "--json"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data == [{
        "artifact": "VISION-001",
        "type": "VISION",
        "status": "Active",
        "canonical_file": "docs/vision/Active/(VISION-001)-Root/(VISION-001)-Root.md",
        "canonical_path": "docs/vision/Active/(VISION-001)-Root",
        "direct_parent": None,
        "placement_state": "root",
        "linked_artifacts": [],
        "depends_on_artifacts": [],
    }]


def test_chart_build_materializes_child_view(tmp_path):
    """chart build should rebuild the graph and materialize direct child links."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    vision_dir = repo_root / "docs" / "vision" / "Active" / "(VISION-001)-Root"
    initiative_dir = repo_root / "docs" / "initiative" / "Active" / "(INITIATIVE-001)-Parent"
    vision_dir.mkdir(parents=True)
    initiative_dir.mkdir(parents=True)
    (vision_dir / "(VISION-001)-Root.md").write_text(
        '---\ntitle: "Root"\nartifact: VISION-001\nstatus: Active\ntrack: standing\n---\n# Vision\n',
        encoding="utf-8",
    )
    (initiative_dir / "(INITIATIVE-001)-Parent.md").write_text(
        '---\ntitle: "Parent"\nartifact: INITIATIVE-001\nstatus: Active\ntrack: container\nparent-vision: VISION-001\n---\n# Initiative\n',
        encoding="utf-8",
    )

    bin_dir = repo_root / ".agents" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "chart.sh").symlink_to(SCRIPTS_DIR / "chart.sh")
    (bin_dir / "chart_cli.py").symlink_to(SCRIPTS_DIR / "chart_cli.py")

    result = subprocess.run(
        ["bash", str(bin_dir / "chart.sh"), "build"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    child_link = vision_dir / "(INITIATIVE-001)-Parent"
    assert child_link.is_symlink()
    assert child_link.resolve() == initiative_dir.resolve()


def test_chart_build_fails_on_duplicate_artifact_ids(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    first = repo_root / "docs" / "spec" / "Active" / "(SPEC-001)-First"
    second = repo_root / "docs" / "spec" / "Proposed" / "(SPEC-001)-Second"
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

    bin_dir = repo_root / ".agents" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "chart.sh").symlink_to(SCRIPTS_DIR / "chart.sh")
    (bin_dir / "chart_cli.py").symlink_to(SCRIPTS_DIR / "chart_cli.py")

    result = subprocess.run(
        ["bash", str(bin_dir / "chart.sh"), "build"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Duplicate artifact IDs detected" in result.stderr
