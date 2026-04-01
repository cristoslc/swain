"""Regression tests for symlinked chart entrypoints."""

from __future__ import annotations

import subprocess
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
