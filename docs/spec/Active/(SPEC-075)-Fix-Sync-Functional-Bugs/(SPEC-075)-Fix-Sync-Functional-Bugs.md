---
title: "Fix swain-sync functional bugs"
artifact: SPEC-075
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: bug
parent-epic: EPIC-031
linked-artifacts:
  - SPEC-039
  - SPEC-072
  - SPEC-079
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Fix swain-sync functional bugs

## Problem Statement

Two high-severity bugs in swain-sync:

1. **Missing allowed-tools:** `allowed-tools: Bash, Read, Edit` is missing `Write` and `Glob`. Step 3 needs to scan the tree for secret-looking files (needs Glob), and the gitignore check may need to write patterns (needs Write).

2. **Fragile worktree pruning:** The worktree cleanup command uses `git worktree list --porcelain | grep -B2 "HEAD"` which matches the current HEAD worktree — in a multi-worktree setup this could target the wrong worktree for removal.

## Acceptance Criteria

**AC-1:** `allowed-tools` includes `Write` and `Glob` alongside existing `Bash, Read, Edit`.

**AC-2:** Worktree pruning identifies the *current* linked worktree path using `git rev-parse --show-toplevel` rather than grepping for HEAD across all worktrees.

**AC-3:** Description updated to mention gitignore hygiene, ADR compliance, and index rebuilding (currently undocumented behaviors).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | Read allowed-tools from frontmatter | |
| AC-2 | Review pruning command logic | |
| AC-3 | Read updated description | |

## Scope & Constraints

**In scope:** `skills/swain-sync/SKILL.md` only.

**Out of scope:** Extracting sections to references/ (that's SPEC-079). Cross-skill path fixes (that's SPEC-072).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Two high-severity bugs from audit |
