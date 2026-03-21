---
title: "Tooling Availability Strategy"
artifact: SPEC-059
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-017
linked-artifacts:
  - SPEC-058
  - SPEC-060
  - SPEC-061
  - SPIKE-015
  - SPIKE-020
depends-on-artifacts: []
addresses: []
evidence-pool: "security-skill-landscape"
source-issue: ""
swain-do: required
---

# Tooling Availability Strategy

## Problem Statement

SPIKE-015 and SPIKE-020 resolved *what* security scanners to use but not *how* to ensure they're present on the operator's machine. swain-security-check depends on external binaries (gitleaks, osv-scanner, trivy, semgrep) that may or may not be installed. Without a clear acquisition strategy per scanner, the skill either fails silently or produces incomplete reports with no guidance on how to fix the gap.

## External Behavior

**Per-scanner availability matrix** — each scanner gets a documented strategy:

| Scanner | Strategy | Rationale |
|---------|----------|-----------|
| gitleaks | Package manager detection (brew/apt/cargo) + swain-doctor diagnostic | Go binary, ~30MB per platform, too large to vendor; widely available in package managers |
| osv-scanner | Package manager detection + swain-doctor diagnostic | Go binary, similar trade-offs to gitleaks |
| trivy | Package manager detection + swain-doctor diagnostic | Go binary, large (~100MB with DB); package manager is the only viable path |
| semgrep | `uv run` / pip detection + swain-doctor diagnostic | Python package; `uv run --with semgrep` for zero-install invocation where uv is available |

**swain-doctor integration:**
- When `swain-security-check` is installed, swain-doctor checks for each enabled scanner binary
- Missing scanners produce a diagnostic with the install command for the detected OS/package manager
- Diagnostic severity: `info` (not blocking) — scanners are optional, skill degrades gracefully

**swain-security-check behavior when scanner is absent:**
- Skip that scanner's vector with a clear warning in the report
- Report which scanners were available vs. missing
- Never fail the overall scan because one scanner is missing

## Acceptance Criteria

- Given gitleaks is not on PATH, when swain-security-check runs, then the secrets vector is skipped with a warning naming the missing tool and install command
- Given swain-doctor runs with gitleaks missing, then a diagnostic is emitted: "gitleaks not found — install with `brew install gitleaks`" (or apt/cargo equivalent based on detected OS)
- Given all scanners are present, when swain-security-check runs, then no availability warnings appear in the report
- Given semgrep is not installed but uv is available, when swain-security-check runs, then semgrep is invoked via `uv run --with semgrep`
- The availability check for each scanner completes in under 1 second (no network calls)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- No vendoring of Go binaries — too large, too many platforms
- No auto-download of binaries (security concern: downloading executables without user consent)
- Python tools (semgrep) may use `uv run` as a zero-install path where uv is available
- The context-file scanner (SPEC-058) is built-in and has no external dependency — it is always available

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | b32f7db | Decomposed from EPIC-017; addresses gap identified in SPIKE-020 review |
