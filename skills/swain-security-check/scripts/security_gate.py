#!/usr/bin/env python3
"""Post-Implementation Security Gate — SPEC-064.

Advisory security checkpoint for swain-do task completion workflow.
For security-sensitive tasks (classified by threat_surface.py), runs a
diff-only scan on changed files and files findings as new tk issues.

Key behaviors:
- Does NOT block task closure — advisory only
- Skips entirely for non-security tasks (zero overhead)
- Uses context_file_scanner (always available) for scanning
- Files findings as tk issues with security-finding tag
- Links filed issues to the originating task via tk link

Zero external deps beyond Python 3 stdlib + sibling modules.
"""

from __future__ import annotations

import subprocess
from typing import Any

from context_file_scanner import scan_file
from threat_surface import detect_threat_surface


# ---------------------------------------------------------------------------
# Severity -> tk priority mapping
# ---------------------------------------------------------------------------

_SEVERITY_TO_PRIORITY: dict[str, str] = {
    "critical": "0",
    "high": "1",
    "medium": "2",
    "low": "3",
}


# ---------------------------------------------------------------------------
# Gate trigger
# ---------------------------------------------------------------------------

def should_run_gate(
    task_title: str,
    task_tags: list[str] | None,
    spec_criteria: str = "",
) -> bool:
    """Determine if the security gate should run for this task.

    Uses threat_surface.detect_threat_surface to classify the task.
    Returns True if the task touches a security-sensitive surface.

    Args:
        task_title: Task title text.
        task_tags: List of task tags (may be None).
        spec_criteria: SPEC acceptance criteria text.

    Returns:
        True if gate should run, False otherwise.
    """
    result = detect_threat_surface(
        title=task_title,
        tags=task_tags,
        spec_criteria=spec_criteria,
    )
    return result.is_security_sensitive


# ---------------------------------------------------------------------------
# Changed file discovery
# ---------------------------------------------------------------------------

def get_changed_files() -> list[str]:
    """Get list of files changed since last commit via git diff.

    Returns file paths from `git diff --name-only HEAD`. On any error
    (git not available, not a repo, etc.) returns an empty list.

    Returns:
        List of relative file paths that changed.
    """
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    if proc.returncode != 0:
        return []

    paths = []
    for line in proc.stdout.split("\n"):
        stripped = line.strip()
        if stripped:
            paths.append(stripped)
    return paths


# ---------------------------------------------------------------------------
# Finding -> ticket filing
# ---------------------------------------------------------------------------

def file_finding_as_ticket(
    finding: dict[str, Any],
    originating_task_id: str,
) -> str | None:
    """File a security finding as a new tk issue and link to originating task.

    Creates a bug-type ticket with the security-finding tag, then links
    it to the originating task. Linking is best-effort — if it fails,
    the ticket ID is still returned.

    Args:
        finding: Finding dict from context_file_scanner (file_path,
                 line_number, category, severity, description, etc.).
        originating_task_id: The tk ID of the task that triggered the gate.

    Returns:
        The new ticket ID on success, or None on failure.
    """
    file_path = finding.get("file_path", "unknown")
    line_number = finding.get("line_number", 0)
    severity = finding.get("severity", "medium")
    description = finding.get("description", "Security finding")
    matched_pattern = finding.get("matched_pattern", "")
    remediation = finding.get("remediation", "")
    category = finding.get("category", "?")

    title = f"Security finding in {file_path}:{line_number} — {description}"
    body_parts = [
        f"**Severity:** {severity}",
        f"**File:** {file_path}:{line_number}",
        f"**Category:** {category}",
        f"**Description:** {description}",
    ]
    if matched_pattern:
        body_parts.append(f"**Matched:** `{matched_pattern}`")
    if remediation:
        body_parts.append(f"**Remediation:** {remediation}")
    body_parts.append(f"**Originating task:** {originating_task_id}")

    body = "\n".join(body_parts)
    priority = _SEVERITY_TO_PRIORITY.get(severity, "2")

    # Create the ticket
    try:
        create_proc = subprocess.run(
            [
                "tk", "create", title,
                "-d", body,
                "-t", "bug",
                "-p", priority,
                "--tags", "security-finding",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if create_proc.returncode != 0:
        return None

    ticket_id = create_proc.stdout.strip()
    if not ticket_id:
        return None

    # Link to originating task (best-effort)
    try:
        subprocess.run(
            ["tk", "link", ticket_id, originating_task_id],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass  # Linking is best-effort

    return ticket_id


# ---------------------------------------------------------------------------
# Gate orchestrator
# ---------------------------------------------------------------------------

def run_gate(
    changed_files: list[str],
    originating_task_id: str,
) -> list[str]:
    """Run the security gate on changed files and file findings as tickets.

    Scans each changed file with context_file_scanner. Any findings are
    filed as new tk issues linked to the originating task.

    Args:
        changed_files: List of file paths to scan (from get_changed_files).
        originating_task_id: The tk ID of the task being completed.

    Returns:
        List of newly created ticket IDs for filed findings.
    """
    if not changed_files:
        return []

    all_findings: list[dict[str, Any]] = []

    for file_path in changed_files:
        try:
            findings = scan_file(file_path)
            all_findings.extend(findings)
        except Exception:
            # If a file can't be scanned, skip it and continue
            continue

    if not all_findings:
        return []

    filed_ids: list[str] = []
    for finding in all_findings:
        ticket_id = file_finding_as_ticket(finding, originating_task_id)
        if ticket_id is not None:
            filed_ids.append(ticket_id)

    return filed_ids
