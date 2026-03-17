#!/usr/bin/env python3
"""Security check orchestrator for swain-security-check (SPEC-060).

Orchestrates all security scanners into a single invocation with a
unified report. Integrates:
- context_file_scanner.py (SPEC-058) — built-in, always runs
- scanner_availability.py (SPEC-059) — checks which external scanners are on PATH
- gitleaks — secret detection
- osv-scanner / trivy — dependency vulnerability scanning
- semgrep — static analysis with ai-best-practices
- Repo hygiene — built-in .gitignore completeness + tracked secret detection

Exit codes:
  0 = no findings
  1 = findings detected
  2 = error

Zero external deps beyond Python 3 stdlib + sibling modules.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any

# Import sibling modules
from context_file_scanner import scan_directory as ctx_scan_directory
from scanner_availability import ScannerResult, check_all_scanners


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ScanResult:
    """Result of a full security scan across all scanners."""

    findings: list[dict[str, Any]] = field(default_factory=list)
    scanners_run: list[str] = field(default_factory=list)
    scanners_skipped: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Finding normalization helpers
# ---------------------------------------------------------------------------

_SEVERITY_ORDER = ("critical", "high", "medium", "low")


def _normalize_severity(severity: str) -> str:
    """Map various severity strings to our canonical set."""
    s = severity.lower().strip()
    mapping = {
        "critical": "critical",
        "error": "critical",
        "high": "high",
        "warning": "medium",
        "medium": "medium",
        "info": "low",
        "low": "low",
    }
    return mapping.get(s, "medium")


def _make_finding(
    scanner: str,
    file_path: str,
    line: int,
    severity: str,
    description: str,
    remediation: str,
    **extra: Any,
) -> dict[str, Any]:
    """Create a normalized finding dict."""
    finding: dict[str, Any] = {
        "scanner": scanner,
        "file_path": file_path,
        "line": line,
        "severity": severity,
        "description": description,
        "remediation": remediation,
    }
    finding.update(extra)
    return finding


# ---------------------------------------------------------------------------
# Gitleaks scanner
# ---------------------------------------------------------------------------

def _run_gitleaks(directory: str, scanner_info: ScannerResult) -> list[dict[str, Any]]:
    """Run gitleaks and return normalized findings."""
    cmd = [
        "gitleaks", "detect",
        "--source", directory,
        "--report-format", "json",
        "--report-path", "/dev/stdout",
        "--no-git",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        raise RuntimeError(f"gitleaks failed: {e}") from e

    if proc.returncode == 0:
        # No findings
        return []

    # Exit 1 = findings present
    try:
        raw = json.loads(proc.stdout) if proc.stdout.strip() else []
    except json.JSONDecodeError:
        return []

    findings = []
    for item in raw:
        findings.append(_make_finding(
            scanner="gitleaks",
            file_path=item.get("File", "unknown"),
            line=item.get("StartLine", 0),
            severity="critical",
            description=item.get("Description", "Secret detected"),
            remediation="Rotate the secret, remove from source control, and add to .gitignore",
        ))
    return findings


# ---------------------------------------------------------------------------
# Semgrep scanner
# ---------------------------------------------------------------------------

def _run_semgrep(directory: str, scanner_info: ScannerResult) -> list[dict[str, Any]]:
    """Run semgrep with ai-best-practices config and return normalized findings."""
    path = scanner_info.path or "semgrep"
    # If path contains "uv run", split it into parts
    if path.startswith("uv run"):
        cmd_parts = path.split() + ["--config", "p/ai-best-practices", "--json", directory]
    else:
        cmd_parts = [path, "--config", "p/ai-best-practices", "--json", directory]

    try:
        proc = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        raise RuntimeError(f"semgrep failed: {e}") from e

    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else {"results": []}
    except json.JSONDecodeError:
        return []

    findings = []
    for item in data.get("results", []):
        severity_raw = item.get("extra", {}).get("severity", "WARNING")
        findings.append(_make_finding(
            scanner="semgrep",
            file_path=item.get("path", "unknown"),
            line=item.get("start", {}).get("line", 0),
            severity=_normalize_severity(severity_raw),
            description=item.get("extra", {}).get("message", item.get("check_id", "Semgrep finding")),
            remediation="Review and fix the flagged pattern per semgrep rule guidance",
        ))
    return findings


# ---------------------------------------------------------------------------
# OSV-scanner
# ---------------------------------------------------------------------------

def _run_osv_scanner(directory: str, scanner_info: ScannerResult) -> list[dict[str, Any]]:
    """Run osv-scanner and return normalized findings."""
    cmd = ["osv-scanner", "--format", "json", "--recursive", directory]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        raise RuntimeError(f"osv-scanner failed: {e}") from e

    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else {"results": []}
    except json.JSONDecodeError:
        return []

    findings = []
    for result_group in data.get("results", []):
        source_path = result_group.get("source", {}).get("path", "unknown")
        for pkg in result_group.get("packages", []):
            for vuln in pkg.get("vulnerabilities", []):
                severity_val = "high"  # Default for known CVEs
                db_specific = vuln.get("database_specific", {})
                if db_specific.get("severity"):
                    severity_val = _normalize_severity(db_specific["severity"])
                findings.append(_make_finding(
                    scanner="osv-scanner",
                    file_path=source_path,
                    line=0,
                    severity=severity_val,
                    description=f"{vuln.get('id', 'Unknown CVE')}: {vuln.get('summary', 'Vulnerability detected')}",
                    remediation="Update the affected dependency to a patched version",
                ))
    return findings


# ---------------------------------------------------------------------------
# Trivy scanner (fallback for osv-scanner)
# ---------------------------------------------------------------------------

def _run_trivy(directory: str, scanner_info: ScannerResult) -> list[dict[str, Any]]:
    """Run trivy and return normalized findings."""
    cmd = ["trivy", "fs", "--format", "json", directory]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        raise RuntimeError(f"trivy failed: {e}") from e

    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else {"Results": []}
    except json.JSONDecodeError:
        return []

    findings = []
    for result_group in data.get("Results", []):
        target = result_group.get("Target", "unknown")
        for vuln in result_group.get("Vulnerabilities", []):
            findings.append(_make_finding(
                scanner="trivy",
                file_path=target,
                line=0,
                severity=_normalize_severity(vuln.get("Severity", "MEDIUM")),
                description=f"{vuln.get('VulnerabilityID', 'Unknown')}: {vuln.get('Title', 'Vulnerability detected')}",
                remediation=f"Update {vuln.get('PkgName', 'package')} to {vuln.get('FixedVersion', 'latest patched version')}",
            ))
    return findings


# ---------------------------------------------------------------------------
# Context-file scanner (built-in)
# ---------------------------------------------------------------------------

def _run_context_file_scanner(directory: str) -> list[dict[str, Any]]:
    """Run the built-in context-file injection scanner."""
    raw_findings = ctx_scan_directory(directory)
    findings = []
    for item in raw_findings:
        # Map context-file scanner categories to remediation guidance
        cat = item.get("category", "?")
        remediation_map = {
            "A": "Remove or rewrite the instruction override pattern",
            "B": "Remove the role override / persona hijacking pattern",
            "C": "Remove the privilege escalation / authority spoofing pattern",
            "D": "Remove the data exfiltration pattern",
            "E": "Remove the persistence mechanism",
            "F": "Remove or decode the obfuscated content for review",
            "G": "Remove hidden Unicode characters and replace with ASCII equivalents",
            "H": "Remove the MCP / config file manipulation pattern",
            "I": "Remove hidden instructions from HTML comments",
            "J": "Remove the external fetch + exec pattern",
        }
        findings.append(_make_finding(
            scanner="context-file-scanner",
            file_path=item.get("file_path", "unknown"),
            line=item.get("line_number", 0),
            severity=item.get("severity", "medium"),
            description=item.get("description", "Context file injection pattern detected"),
            remediation=remediation_map.get(cat, "Review and remove the suspicious pattern"),
            category=cat,
        ))
    return findings


# ---------------------------------------------------------------------------
# Repo hygiene (built-in)
# ---------------------------------------------------------------------------

_EXPECTED_GITIGNORE_PATTERNS = [
    (".env", "Secrets in .env files may be committed"),
    ("node_modules", "node_modules/ should be ignored"),
    ("__pycache__", "__pycache__/ should be ignored"),
    (".DS_Store", ".DS_Store files should be ignored"),
]


def _check_gitignore(directory: str) -> list[dict[str, Any]]:
    """Check .gitignore completeness."""
    gitignore_path = os.path.join(directory, ".gitignore")
    findings = []

    if not os.path.isfile(gitignore_path):
        findings.append(_make_finding(
            scanner="repo-hygiene",
            file_path=".gitignore",
            line=0,
            severity="medium",
            description="Missing .gitignore file — secrets and build artifacts may be committed",
            remediation="Create a .gitignore file with patterns for .env, node_modules, __pycache__, .DS_Store",
        ))
        return findings

    try:
        with open(gitignore_path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return findings

    for pattern, message in _EXPECTED_GITIGNORE_PATTERNS:
        if pattern not in content:
            findings.append(_make_finding(
                scanner="repo-hygiene",
                file_path=".gitignore",
                line=0,
                severity="medium",
                description=f".gitignore missing '{pattern}' pattern — {message}",
                remediation=f"Add '{pattern}' to .gitignore",
            ))

    return findings


def _check_tracked_env_files(directory: str) -> list[dict[str, Any]]:
    """Check for tracked .env files (not .env.example) via git ls-files."""
    findings = []

    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=directory,
        )
        if proc.returncode != 0:
            return findings
    except (subprocess.TimeoutExpired, OSError):
        return findings

    for line in proc.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        basename = os.path.basename(line)
        # Match .env, .env.local, .env.production, etc. but NOT .env.example
        if basename.startswith(".env") and ".example" not in basename and basename != ".env.example":
            # Exclude if it's just ".env.example" in a subdir
            if ".example" not in line:
                findings.append(_make_finding(
                    scanner="repo-hygiene",
                    file_path=line,
                    line=0,
                    severity="critical",
                    description=f"Tracked .env file '{line}' — secrets may be in git history",
                    remediation=f"Remove '{line}' from git tracking: git rm --cached {line}",
                ))

    return findings


def _run_repo_hygiene(directory: str) -> list[dict[str, Any]]:
    """Run all built-in repo hygiene checks."""
    findings = []
    findings.extend(_check_gitignore(directory))
    findings.extend(_check_tracked_env_files(directory))
    return findings


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_scan(directory: str) -> ScanResult:
    """Run all available security scanners against a directory.

    Checks scanner availability, runs available scanners, normalizes
    findings, and compiles results.

    Args:
        directory: Path to the project directory to scan.

    Returns:
        ScanResult with all findings, scanner status, and any errors.
    """
    result = ScanResult()
    directory = os.path.abspath(directory)

    # Check external scanner availability
    availability = check_all_scanners()
    scanner_map: dict[str, ScannerResult] = {s.name: s for s in availability}

    # --- External scanners ---

    # Gitleaks (secrets)
    gitleaks = scanner_map.get("gitleaks")
    if gitleaks and gitleaks.available:
        try:
            result.findings.extend(_run_gitleaks(directory, gitleaks))
            result.scanners_run.append("gitleaks")
        except RuntimeError as e:
            result.errors.append(str(e))
    elif gitleaks:
        result.scanners_skipped.append({
            "name": "gitleaks",
            "install_hint": gitleaks.install_hint or "",
        })

    # Dependency scanner: prefer osv-scanner, fallback to trivy
    osv = scanner_map.get("osv-scanner")
    trivy = scanner_map.get("trivy")
    if osv and osv.available:
        try:
            result.findings.extend(_run_osv_scanner(directory, osv))
            result.scanners_run.append("osv-scanner")
        except RuntimeError as e:
            result.errors.append(str(e))
    elif trivy and trivy.available:
        try:
            result.findings.extend(_run_trivy(directory, trivy))
            result.scanners_run.append("trivy")
        except RuntimeError as e:
            result.errors.append(str(e))
    else:
        # Both missing — skip both
        if osv:
            result.scanners_skipped.append({
                "name": "osv-scanner",
                "install_hint": osv.install_hint or "",
            })
        if trivy:
            result.scanners_skipped.append({
                "name": "trivy",
                "install_hint": trivy.install_hint or "",
            })

    # Semgrep (static analysis)
    semgrep = scanner_map.get("semgrep")
    if semgrep and semgrep.available:
        try:
            result.findings.extend(_run_semgrep(directory, semgrep))
            result.scanners_run.append("semgrep")
        except RuntimeError as e:
            result.errors.append(str(e))
    elif semgrep:
        result.scanners_skipped.append({
            "name": "semgrep",
            "install_hint": semgrep.install_hint or "",
        })

    # --- Built-in scanners (always run) ---

    # Context-file scanner
    result.findings.extend(_run_context_file_scanner(directory))
    result.scanners_run.append("context-file-scanner")

    # Repo hygiene
    result.findings.extend(_run_repo_hygiene(directory))
    result.scanners_run.append("repo-hygiene")

    return result


# ---------------------------------------------------------------------------
# Severity bucketing
# ---------------------------------------------------------------------------

def bucket_by_severity(findings: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group findings by severity level.

    Returns a dict with keys: critical, high, medium, low.
    Each key maps to a list of findings at that severity.
    Empty severity levels are always present.
    """
    buckets: dict[str, list[dict[str, Any]]] = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
    }
    for finding in findings:
        sev = finding.get("severity", "medium")
        if sev in buckets:
            buckets[sev].append(finding)
        else:
            buckets["medium"].append(finding)
    return buckets


# ---------------------------------------------------------------------------
# Summary line
# ---------------------------------------------------------------------------

def format_summary_line(findings: list[dict[str, Any]], scanners_run: list[str]) -> str:
    """Format a summary line with severity counts and scanner count.

    Example: "1 critical, 2 high, 0 medium, 0 low findings across 4 scanners"
    """
    buckets = bucket_by_severity(findings)
    parts = [f"{len(buckets[sev])} {sev}" for sev in _SEVERITY_ORDER]
    total = len(findings)
    n_scanners = len(scanners_run)
    return f"{', '.join(parts)} findings ({total} total) across {n_scanners} scanners"


# ---------------------------------------------------------------------------
# JSON report
# ---------------------------------------------------------------------------

def format_json_report(result: ScanResult) -> str:
    """Format scan results as a JSON report string.

    Structure:
    {
        "summary": {"critical": N, "high": N, "medium": N, "low": N, "total": N},
        "scanners_run": [...],
        "scanners_skipped": [...],
        "findings": [...]
    }
    """
    buckets = bucket_by_severity(result.findings)
    report = {
        "summary": {
            "critical": len(buckets["critical"]),
            "high": len(buckets["high"]),
            "medium": len(buckets["medium"]),
            "low": len(buckets["low"]),
            "total": len(result.findings),
        },
        "scanners_run": result.scanners_run,
        "scanners_skipped": result.scanners_skipped,
        "findings": result.findings,
    }
    if result.errors:
        report["errors"] = result.errors
    return json.dumps(report, indent=2)


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def format_markdown_report(result: ScanResult) -> str:
    """Format scan results as a markdown report string."""
    lines: list[str] = []
    summary = format_summary_line(result.findings, result.scanners_run)

    lines.append("# Security Scan Report")
    lines.append("")
    lines.append(f"**Summary:** {summary}")
    lines.append("")

    # Scanners run
    lines.append("## Scanners")
    lines.append("")
    for name in result.scanners_run:
        lines.append(f"- [x] {name}")
    for skipped in result.scanners_skipped:
        name = skipped["name"]
        hint = skipped.get("install_hint", "")
        lines.append(f"- [ ] {name} — skipped (not found)")
        if hint:
            lines.append(f"  - Install: `{hint}`")
    lines.append("")

    # Findings by severity
    if result.findings:
        buckets = bucket_by_severity(result.findings)
        for sev in _SEVERITY_ORDER:
            sev_findings = buckets[sev]
            if not sev_findings:
                continue
            lines.append(f"## {sev.capitalize()} ({len(sev_findings)})")
            lines.append("")
            for f in sev_findings:
                scanner = f.get("scanner", "unknown")
                fpath = f.get("file_path", "unknown")
                line_num = f.get("line", 0)
                desc = f.get("description", "")
                remed = f.get("remediation", "")
                lines.append(f"### {desc}")
                lines.append("")
                lines.append(f"- **Scanner:** {scanner}")
                lines.append(f"- **File:** `{fpath}`:{line_num}")
                lines.append(f"- **Remediation:** {remed}")
                lines.append("")
    else:
        lines.append("## No findings")
        lines.append("")
        lines.append("No security findings detected. All scanned vectors are clean.")
        lines.append("")

    # Errors
    if result.errors:
        lines.append("## Errors")
        lines.append("")
        for err in result.errors:
            lines.append(f"- {err}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code.

    Exit codes:
      0 = no findings
      1 = findings detected
      2 = error
    """
    parser = argparse.ArgumentParser(
        description="Run all security scanners and produce a unified report.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Directories to scan (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output report as JSON",
    )

    args = parser.parse_args(argv)

    all_findings: list[dict[str, Any]] = []
    had_error = False
    combined_result = ScanResult()

    for path in args.paths:
        if not os.path.isdir(path):
            print(f"Error: directory not found: {path}", file=sys.stderr)
            had_error = True
            continue

        result = run_scan(path)
        combined_result.findings.extend(result.findings)
        # Merge scanners_run (unique)
        for s in result.scanners_run:
            if s not in combined_result.scanners_run:
                combined_result.scanners_run.append(s)
        # Merge scanners_skipped (unique by name)
        existing_skipped = {s["name"] for s in combined_result.scanners_skipped}
        for s in result.scanners_skipped:
            if s["name"] not in existing_skipped:
                combined_result.scanners_skipped.append(s)
                existing_skipped.add(s["name"])
        combined_result.errors.extend(result.errors)

    if had_error and not combined_result.findings:
        return 2

    if args.json_output:
        print(format_json_report(combined_result))
    else:
        print(format_markdown_report(combined_result))

    if combined_result.findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
