#!/usr/bin/env python3
"""Lightweight security diagnostic for swain-doctor session-start flow.

SPEC-061: Runs critical-only context-file scanning on AGENTS.md/CLAUDE.md
and checks for tracked .env files. Must complete in <3 seconds.

This module:
1. Scans context files for CRITICAL categories only: D, F, G, H
   (exfiltration, encoding obfuscation, hidden Unicode, MCP manipulation)
2. Checks for tracked .env files in git history
3. Outputs diagnostics in swain-doctor format (WARN/CRIT)
4. Silent pass when no issues found
5. Advisory only — does not block session start (always exits 0)

Exit codes:
  0 = no findings (clean)
  1 = findings detected (advisory)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import Any

# Import the context file scanner from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from context_file_scanner import scan_content  # noqa: E402


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Only these categories are checked during the lightweight doctor scan
CRITICAL_CATEGORIES = {"D", "F", "G", "H"}

# Context file names to scan at the repo root
CONTEXT_FILES = ["AGENTS.md", "CLAUDE.md"]

# Glob patterns for SKILL.md files
SKILL_DIRS = [
    os.path.join(".claude", "skills"),
    os.path.join(".agents", "skills"),
    os.path.join("skills"),
]


# ---------------------------------------------------------------------------
# Context-file scanning (critical categories only)
# ---------------------------------------------------------------------------


def _discover_context_files(repo_dir: str) -> list[str]:
    """Discover context files to scan in the repo.

    Finds AGENTS.md, CLAUDE.md at repo root, and SKILL.md files in
    known skill directories.
    """
    found: list[str] = []

    # Root context files
    for name in CONTEXT_FILES:
        path = os.path.join(repo_dir, name)
        if os.path.isfile(path):
            found.append(path)

    # SKILL.md files in skill directories
    for skill_dir in SKILL_DIRS:
        full_dir = os.path.join(repo_dir, skill_dir)
        if not os.path.isdir(full_dir):
            continue
        for entry in os.listdir(full_dir):
            skill_path = os.path.join(full_dir, entry, "SKILL.md")
            if os.path.isfile(skill_path):
                found.append(skill_path)

    return sorted(found)


def scan_context_files_critical(file_paths: list[str]) -> list[dict[str, Any]]:
    """Scan the given context files, returning only critical-category findings.

    Filters to categories D, F, G, H only.
    """
    findings: list[dict[str, Any]] = []

    for file_path in file_paths:
        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError:
            continue

        all_findings = scan_content(content, file_path=file_path)
        critical = [f for f in all_findings if f["category"] in CRITICAL_CATEGORIES]
        findings.extend(critical)

    return findings


# ---------------------------------------------------------------------------
# Tracked .env file detection
# ---------------------------------------------------------------------------


def detect_tracked_env_files(repo_dir: str | None = None) -> list[str]:
    """Detect tracked .env files in git history.

    Returns list of tracked file paths matching .env pattern,
    excluding .env.example files.
    """
    cmd = ["git", "ls-files"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=repo_dir,
            timeout=5,
        )
        if result.returncode != 0:
            return []
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []

    tracked_files = result.stdout.strip().splitlines()
    env_pattern = re.compile(r"\.env($|\.)")
    example_pattern = re.compile(r"\.example$")

    env_files = []
    for f in tracked_files:
        basename = os.path.basename(f)
        if env_pattern.search(basename) and not example_pattern.search(basename):
            env_files.append(f)

    return env_files


# ---------------------------------------------------------------------------
# Diagnostic formatting
# ---------------------------------------------------------------------------


def format_diagnostics(findings: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Format scanner findings as swain-doctor diagnostics.

    Maps scanner severity to diagnostic severity:
      critical -> CRIT
      high     -> WARN
      medium   -> WARN
      low      -> INFO
    """
    severity_map = {
        "critical": "CRIT",
        "high": "WARN",
        "medium": "WARN",
        "low": "INFO",
    }

    diagnostics: list[dict[str, str]] = []
    for finding in findings:
        sev = severity_map.get(finding["severity"], "WARN")
        file_path = finding["file_path"]
        line_num = finding["line_number"]
        desc = finding["description"]
        cat = finding["category"]

        message = f"[{cat}] {file_path}:{line_num} — {desc}"
        diagnostics.append({"severity": sev, "message": message})

    return diagnostics


def format_env_diagnostics(tracked_envs: list[str]) -> list[dict[str, str]]:
    """Format tracked .env file findings as swain-doctor diagnostics."""
    diagnostics: list[dict[str, str]] = []
    for env_file in tracked_envs:
        message = (
            f"Tracked .env file: {env_file} — "
            f"remove with `git rm --cached {env_file}` and add to .gitignore. "
            f"For history cleanup, use BFG Repo-Cleaner or git filter-branch."
        )
        diagnostics.append({"severity": "WARN", "message": message})
    return diagnostics


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main(repo_dir: str | None = None) -> int:
    """Run lightweight security diagnostics.

    Returns:
      0 = no findings
      1 = findings detected (advisory)
    """
    if repo_dir is None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            repo_dir = result.stdout.strip() if result.returncode == 0 else os.getcwd()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            repo_dir = os.getcwd()

    all_diagnostics: list[dict[str, str]] = []

    # 1. Context-file scan (critical categories only)
    context_files = _discover_context_files(repo_dir)
    findings = scan_context_files_critical(context_files)
    all_diagnostics.extend(format_diagnostics(findings))

    # 2. Tracked .env file detection
    tracked_envs = detect_tracked_env_files(repo_dir=repo_dir)
    all_diagnostics.extend(format_env_diagnostics(tracked_envs))

    # Output diagnostics
    if all_diagnostics:
        for diag in all_diagnostics:
            print(f"security-check [{diag['severity']}]: {diag['message']}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
