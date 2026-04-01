"""Regression tests for changelog rendering."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "skills" / "swain-release" / "scripts" / "render_changelog.py"


def test_symlinked_entrypoint_resolves_default_template(tmp_path):
    """The .agents/bin symlink should still find the bundled template."""
    bin_dir = tmp_path / ".agents" / "bin"
    bin_dir.mkdir(parents=True)

    entrypoint = bin_dir / "render_changelog.py"
    entrypoint.symlink_to(SCRIPT_PATH)

    data_path = tmp_path / "changelog.json"
    data_path.write_text(
        json.dumps(
            {
                "version": "0.99.0-alpha",
                "date": "2026-04-01",
                "features": [{"heading": "Test Feature", "body": "Rendered from template."}],
                "roadmap": [],
                "research": [],
                "supporting": [],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(entrypoint), str(data_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "## [0.99.0-alpha] - 2026-04-01" in result.stdout
    assert "#### Test Feature" in result.stdout
