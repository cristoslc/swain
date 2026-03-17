---
title: "Post-Implementation Security Gate"
artifact: SPEC-064
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-023
linked-artifacts:
  - EPIC-017
depends-on-artifacts:
  - SPEC-060
  - SPEC-062
addresses: []
evidence-pool: "security-skill-landscape"
source-issue: ""
swain-do: required
---

# Post-Implementation Security Gate

## Problem Statement

Security findings discovered after code is written need a structured path into the task tracking system. Currently, swain-do's "landing the plane" workflow runs tests and lints but has no security checkpoint. For security-sensitive tasks, a lightweight security gate should run at task completion, and findings should be filed as new tk issues rather than silently dropped.

## External Behavior

**Trigger:** During swain-do's task completion workflow (before `tk close`), when the task was classified as security-sensitive by SPEC-062.

**Gate behavior:**
1. For security-sensitive tasks: invoke swain-security-check (SPEC-060) in diff-only mode — scan only files changed during the task
2. For non-security-sensitive tasks: skip the gate entirely (no overhead)
3. Collect findings from the diff scan

**Finding disposition:**
- Findings are filed as new tk issues with tag `security-finding`, linked to the original task
- The original task is NOT blocked — it can still be closed
- Filed issues have severity mapped from the scanner finding severity
- Each filed issue includes: the finding description, file path, line number, and suggested remediation

**Output:** Summary of findings filed:
```
Security gate: 2 findings filed as new issues
  - tk-042: High — hardcoded API key in config.py:23 (gitleaks)
  - tk-043: Medium — unvalidated user input in handler.py:45 (semgrep)
```

## Acceptance Criteria

- Given a security-sensitive task with a leaked secret in changed files, when the task completes, then a new tk issue is filed with the finding
- Given a non-security-sensitive task, when the task completes, then no security gate runs
- Given a security-sensitive task with no findings, when the task completes, then the gate runs but files no issues
- Filed tk issues include the tag `security-finding` and a dependency link to the originating task
- The gate does not block task closure — findings are advisory

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Diff-only mode — scans only changed files, not the entire project
- Depends on swain-security-check (SPEC-060) for the actual scanning
- The gate is best-effort — if swain-security-check is not installed, the gate is skipped with a warning
- Does not replace full project scans — complements them with targeted per-task checks

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | b32f7db | Decomposed from EPIC-023; depends on EPIC-017 for scanner |
