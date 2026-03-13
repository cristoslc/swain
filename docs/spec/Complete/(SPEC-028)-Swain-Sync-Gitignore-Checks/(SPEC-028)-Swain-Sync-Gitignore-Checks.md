---
title: "swain-sync Gitignore Checks"
artifact: SPEC-028
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
source-issue: "github:cristoslc/swain#39"
parent-epic: ""
swain-do: required
addresses: []
linked-artifacts: []
depends-on-artifacts: []
implementation-commits: 1912844
---

# swain-sync Gitignore Checks

## Problem Statement

`swain-sync` stages and commits changes without verifying `.gitignore` configuration. This can lead to accidentally tracking files that should be ignored (build artifacts, secrets, OS-specific files), which is hard to clean up after the fact.

Source: [GitHub Issue #39](https://github.com/cristoslc/swain/issues/39)

## Acceptance Criteria

1. Before committing, swain-sync checks for `.gitignore` existence and warns if missing
2. Common patterns (`.env`, `node_modules/`, `__pycache__/`, `.DS_Store`) are checked and missing ones are reported
3. Warnings are advisory — they do not block the commit
4. Check is added as a new step between staging (Step 3) and commit message generation (Step 4)

## Scope

In scope:
- Add gitignore validation step to swain-sync SKILL.md
- Check for .gitignore existence
- Check for commonly ignored patterns
- Advisory warnings (not blocking)

Out of scope:
- Auto-generating .gitignore files
- Checking staged files against gitignore patterns
- Language-specific gitignore templates

## Verification

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | .gitignore existence check | PASS | Step 3.5 added to SKILL.md |
| 2 | Common pattern check | PASS | Pattern list in Step 3.5 |
| 3 | Advisory warnings only | PASS | "Continue regardless" instruction in Step 3.5 |
| 4 | Positioned between staging and commit msg | PASS | Step 3.5 location |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Complete | 2026-03-13 | 1912844 | Enhancement — direct to Complete |
