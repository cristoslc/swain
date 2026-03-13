#!/usr/bin/env python3
"""specgraph — Artifact dependency graph engine for swain.

Usage: specgraph.py <command> [args] [--all] [--all-edges]

See specgraph-guide.md for full command reference.
"""

import sys
from pathlib import Path

# Add the scripts directory to sys.path so the specgraph package is importable
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from specgraph.cli import main

if __name__ == "__main__":
    main()
