---
title: "Pre-Commit Verification in swain-sync"
artifact: SPEC-024
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
implementation-commits:
  - c70bfb0
type: feature
parent-epic: EPIC-012
linked-artifacts:
  - SPIKE-015
  - SPEC-023
depends-on-artifacts:
  - SPEC-023
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#24"
swain-do: required
---

# Pre-Commit Verification in swain-sync

## Problem Statement

swain-sync currently commits without verifying that pre-commit hooks ran and passed. When hooks are configured (via SPEC-023), swain-sync should verify they executed successfully before proceeding with the commit, and surface clear diagnostics when they fail.

## External Behavior

### During commit (Step 5 of swain-sync)

After staging changes (Step 3) and generating the commit message (Step 4), swain-sync:

1. Runs `git commit` which triggers pre-commit hooks automatically
2. If hooks pass: proceed to push (Step 6)
3. If hooks fail:
   - Parse the hook output to identify which scanner(s) flagged findings
   - Present findings in a structured format:
     ```
     Pre-commit hook failed:
       gitleaks: 2 findings (AWS key in config.py:42, GitHub token in .env)

     Fix the findings and run /swain-sync again.
     Suppress false positives: add to .gitleaksignore
     ```
   - Stop execution (do not push)
   - Do not retry automatically — the user/agent must fix and re-invoke

### Hook bypass

swain-sync does NOT support `--no-verify` or any hook bypass. If pre-commit hooks are configured, they always run. To disable a scanner, update `swain.settings.json` and re-run `swain-init`.

### When no hooks are configured

If `.pre-commit-config.yaml` doesn't exist or `pre-commit` isn't installed, swain-sync proceeds normally (current behavior). It logs a one-time warning:
```
WARN: No pre-commit hooks configured. Run /swain-init to set up security scanning.
```

## Acceptance Criteria

- **Given** pre-commit hooks are configured and pass, **when** swain-sync commits, **then** the commit succeeds and push proceeds
- **Given** pre-commit hooks are configured and fail, **when** swain-sync commits, **then** it reports the findings clearly and stops before pushing
- **Given** a hook failure, **when** the output is presented, **then** it identifies which scanner failed and what was found
- **Given** no pre-commit hooks are configured, **when** swain-sync runs, **then** it proceeds normally with a one-time warning suggesting /swain-init
- **Given** any invocation of swain-sync, **when** hooks exist, **then** there is no way to bypass them (no --no-verify support)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Does not install or configure hooks (that's SPEC-023)
- Does not implement scanner-specific output parsing beyond what pre-commit provides
- The hook output parsing is best-effort — if a scanner's output format is unrecognized, show raw output
- Depends on SPEC-023 being implemented first (hooks must exist to verify them)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-13 | 8ec761d | Initial creation |
| Complete | 2026-03-13 | 62662e6 | Step 4.5 and hook failure handling added to swain-sync |
