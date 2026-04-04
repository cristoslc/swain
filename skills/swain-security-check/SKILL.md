---
name: swain-security-check
description: "Run all security scanners against the project and produce a unified, severity-bucketed report. Orchestrates gitleaks (secrets), osv-scanner/trivy (dependency vulns), semgrep (static analysis), context-file injection scanner (built-in), and repo hygiene checks (built-in). Missing scanners are skipped with install hints — the scan always completes. Triggers on: 'security check', 'security scan', 'run security', 'scan for secrets', 'check for vulnerabilities', 'security audit', 'audit dependencies', 'check secrets', 'find vulnerabilities', 'scan codebase'."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Grep, Glob
metadata:
  short-description: Unified security scanning orchestrator
  version: 1.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: medium -->

# Security Check

<!-- session-check: SPEC-121 -->
Before proceeding with any state-changing operation, check for an active session:
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If the JSON output has `"status"` other than `"active"`, inform the operator: "No active session — start one with `/swain-init`?" Proceed if they dismiss.

Unified security scanning orchestrator. Checks scanner availability, runs all available scanners against the project, normalizes findings into a severity-bucketed report, and presents results in both JSON and markdown formats.

## When invoked

Run the security check script:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SEC_SCRIPT="$REPO_ROOT/.agents/bin/security_check.py"
[ -n "$SEC_SCRIPT" ] && python3 "$SEC_SCRIPT" . || echo "security_check.py not found"
```

For JSON output:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SEC_SCRIPT="$REPO_ROOT/.agents/bin/security_check.py"
[ -n "$SEC_SCRIPT" ] && python3 "$SEC_SCRIPT" --json . || echo "security_check.py not found"
```

## Orchestration flow

1. **Check availability** — detect which external scanners are installed (per SPEC-059)
2. **Run scanners** — invoke each available scanner against the project:
   - **gitleaks** (secrets) — `gitleaks detect --source . --report-format json`
   - **osv-scanner** or **trivy** (dependency vulns) — scan lockfiles and manifests
   - **semgrep** (static analysis) — `semgrep --config p/ai-best-practices`
   - **Context-file scanner** (built-in, always runs) — scan all agentic context files for injection patterns (SPEC-058, categories A-J)
   - **Repo hygiene** (built-in, always runs) — .gitignore completeness, tracked .env files
3. **Normalize** — map all findings to unified format (scanner, file, line, severity, description, remediation)
4. **Report** — severity-bucketed output (critical/high/medium/low) with summary line

## Graceful degradation

Missing external scanners are **skipped with a warning** — the scan never fails due to a missing tool. The two built-in scanners (context-file scanner and repo hygiene) always run, so the scan always produces results.

Each skipped scanner includes an install hint in the report.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | No findings |
| 1 | Findings present |
| 2 | Error (e.g., invalid path) |

## Report format

### Severity levels

- **Critical** — secrets in source, tracked .env files, instruction override patterns
- **High** — role hijacking, privilege escalation, encoding obfuscation
- **Medium** — missing .gitignore patterns, dependency vulnerabilities
- **Low** — informational findings

### Per-finding fields

| Field | Description |
|-------|-------------|
| scanner | Which scanner produced the finding |
| file_path | File where the finding was detected |
| line | Line number (0 if not applicable) |
| severity | critical, high, medium, or low |
| description | What was found |
| remediation | How to fix it |

### Summary line

Example: `1 critical, 2 high, 0 medium, 0 low findings (3 total) across 4 scanners`

## Integration points

- **swain-doctor** (SPEC-061) — runs a lightweight context-file scan during session startup
- **swain-do** (SPEC-063) — pre-claim security briefing for security-sensitive tasks
- **swain-init** — configures gitleaks pre-commit hook during project onboarding
- **External security skills** (SPEC-065) — hook interface for third-party security skills

## External Security Skill Hook Interface
Read [references/external-hook-api.md](references/external-hook-api.md) for the hook registration contract, event schema, and integration patterns.

## Dependencies

- SPEC-058: Context-file injection scanner (`context_file_scanner.py`)
- SPEC-059: Scanner availability detection (`scanner_availability.py`)
- SPEC-065: External security skill hook interface (`external_hooks.py`)
