#!/usr/bin/env python3
"""Context-File Injection Heuristic Scanner.

Scans agentic coding context files (AGENTS.md, CLAUDE.md, .cursorrules,
skill SKILL.md files, etc.) for prompt injection patterns using regex
heuristics.

Categories A-J per SPIKE-020:
  A: Instruction override
  B: Role override / persona hijacking
  C: Privilege escalation / authority spoofing
  D: Data exfiltration (explicit)
  E: Persistence mechanisms
  F: Base64 / encoding obfuscation
  G: Hidden Unicode (byte-level)
  H: MCP / config file manipulation
  I: HTML comment injection
  J: External fetch + exec

Exit codes:
  0 = no findings
  1 = findings detected
  2 = error
"""

from __future__ import annotations

import json
import sys
from typing import Any


def scan_content(content: str, file_path: str = "<stdin>") -> list[dict[str, Any]]:
    """Scan text content for injection patterns.

    Returns a list of finding dicts with keys:
      file_path, line_number, category, severity, matched_pattern, description
    """
    # TODO: implement categories A-J
    return []


def scan_file(file_path: str) -> list[dict[str, Any]]:
    """Scan a single file for injection patterns."""
    # TODO: implement
    return []


def discover_context_files(directory: str) -> list[str]:
    """Discover agentic runtime context files in a directory tree."""
    # TODO: implement
    return []


def scan_directory(directory: str) -> list[dict[str, Any]]:
    """Scan all context files in a directory tree."""
    # TODO: implement
    return []


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    # TODO: implement
    return 2


if __name__ == "__main__":
    sys.exit(main())
