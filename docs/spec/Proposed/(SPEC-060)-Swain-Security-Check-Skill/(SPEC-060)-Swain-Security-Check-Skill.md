---
title: "swain-security-check Skill"
artifact: SPEC-060
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-017
linked-artifacts:
  - SPEC-058
  - SPEC-059
  - SPEC-061
  - SPEC-064
  - SPIKE-015
  - SPIKE-020
depends-on-artifacts:
  - SPEC-058
  - SPEC-059
addresses: []
evidence-pool: "security-skill-landscape"
source-issue: ""
swain-do: required
---

# swain-security-check Skill

## Problem Statement

The operator needs a single invocation that scans a project across all security vectors and produces a unified, actionable report. Currently, each scanner (gitleaks, osv-scanner, trivy, semgrep, context-file scanner) must be invoked separately with different CLIs and output formats. No orchestration layer exists to normalize and compile their output.

## External Behavior

**Invocation:** `/swain-security-check` (user-invocable skill)

**Orchestration flow:**
1. Check scanner availability (per SPEC-059 strategy)
2. Run each available scanner against the project:
   - gitleaks (secrets) — `gitleaks detect --source . --report-format json`
   - osv-scanner or trivy (dependency vulns) — scan lockfiles/manifests
   - semgrep + ai-best-practices (LLM code patterns) — `semgrep --config p/ai-best-practices`
   - Context-file scanner (SPEC-058) — scan all agentic runtime context files
   - Repo-level hygiene — .gitignore completeness, tracked secrets in git history
3. Normalize all findings into a unified format
4. Compile and present the report

**Report format:**
- Severity-bucketed (critical, high, medium, low)
- Per-finding: source scanner, file path, line number, description, remediation step
- Summary line: "X critical, Y high, Z medium, W low findings across N scanners"
- Machine-readable JSON output alongside human-readable markdown

**Exit codes:** 0 = no findings, 1 = findings present, 2 = error

## Acceptance Criteria

- Given a project with a leaked API key in a tracked file, when `/swain-security-check` runs, then gitleaks reports the finding in the unified report with a remediation step
- Given a project with a known CVE in package.json dependencies, when scanned with osv-scanner available, then the vulnerability appears in the report
- Given a project with `AGENTS.md` containing injection patterns, when scanned, then context-file findings appear in the report alongside scanner findings
- Given a project with Semgrep available and LLM API calls using unvalidated user input, when scanned, then the ai-best-practices finding appears
- Given gitleaks is missing but other scanners are present, when scanned, then the report shows secrets vector as "skipped (gitleaks not found)" and all other vectors report normally
- The skill file (`skills/swain-security-check/SKILL.md`) is a valid swain skill with proper frontmatter
- JSON and markdown report outputs are both produced

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Orchestration only — does not implement scanner logic (delegates to external tools + SPEC-058)
- No automated remediation — report only
- Repo-level hygiene checks (gitignore, tracked secrets) are built-in heuristics, not external tools
- Depends on SPEC-058 (context-file scanner) and SPEC-059 (tooling availability) being implemented first

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | b32f7db | Decomposed from EPIC-017; the orchestration shell per SPIKE-020 hybrid verdict |
