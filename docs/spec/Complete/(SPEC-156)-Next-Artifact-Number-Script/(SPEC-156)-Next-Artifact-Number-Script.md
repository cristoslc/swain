---
title: "next-artifact-number.sh — Core Allocator Script"
artifact: SPEC-156
track: implementable
status: Complete
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
priority-weight: ""
type: feature
parent-epic: EPIC-043
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# next-artifact-number.sh — Core Allocator Script

## Problem Statement

Artifact number allocation is currently ad-hoc — the agent scans `docs/<type>/` in the local working tree and picks max+1. In worktree-based workflows, each worktree has an isolated copy of `docs/`, so two concurrent sessions can allocate the same number. There is no single source of truth.

## Desired Outcomes

- Agents call one script and get the next safe number for any artifact type — no scanning logic reimplemented per-caller.
- Operators working in multiple worktrees never encounter duplicate artifact numbers after merge.

## External Behavior

**Interface:**
```
next-artifact-number.sh <TYPE>
```

Where `<TYPE>` is one of: `SPEC`, `EPIC`, `INITIATIVE`, `VISION`, `SPIKE`, `ADR`, `PERSONA`, `RUNBOOK`, `DESIGN`, `JOURNEY`, `TRAIN`.

**Output:** A single integer (the next available number), zero-padded to 3 digits, on stdout. Example: `156`.

**Algorithm:**
1. Enumerate all worktrees via `git worktree list --porcelain`.
2. For each worktree path, scan `<worktree>/docs/<type-lowercase>/` recursively for directories and files matching `(<TYPE>-NNN)`.
3. Also scan `git show trunk:docs/<type-lowercase>/` to catch numbers committed to trunk but not yet in any worktree's working tree.
4. Take the max across all sources.
5. Return max + 1.

**Preconditions:**
- Must be invoked from within a git repository (or worktree).
- `trunk` branch must exist (or the script falls back to the current branch's remote tracking branch).

**Error behavior:**
- If `<TYPE>` is unrecognized, exit 1 with usage message on stderr.
- If no existing artifacts are found for the type, return `001`.

## Acceptance Criteria

- **Given** a repo with SPEC-001 through SPEC-155 on trunk, **when** `next-artifact-number.sh SPEC` is called, **then** it outputs `156`.
- **Given** a worktree that has created SPEC-160 locally (not yet merged), **when** `next-artifact-number.sh SPEC` is called from the main worktree, **then** it outputs `161` (sees the worktree's SPEC-160).
- **Given** a worktree that has created SPEC-160 locally, **when** `next-artifact-number.sh SPEC` is called from that same worktree, **then** it also outputs `161`.
- **Given** no existing artifacts of type TRAIN, **when** `next-artifact-number.sh TRAIN` is called, **then** it outputs `001`.
- **Given** an invalid type argument, **when** the script is called, **then** it exits 1 with a usage message.
- **Given** the script is called outside a git repo, **then** it exits 1 with an error message.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Outputs 156 for SPEC-001..155 on trunk | `test-next-artifact-number.sh` Test 4: local working tree scan | Pass |
| Sees SPEC-160 in other worktree, returns 161 | `test-next-artifact-number.sh` Test 5: cross-worktree scan (main→wt) | Pass |
| From worktree itself, also returns 161 | `test-next-artifact-number.sh` Test 5: cross-worktree scan (wt→wt) | Pass |
| Returns 001 for empty type (TRAIN) | `test-next-artifact-number.sh` Test 3: no existing artifacts | Pass |
| Invalid type exits non-zero | `test-next-artifact-number.sh` Test 1: invalid type | Pass |
| Outside git repo exits non-zero | `test-next-artifact-number.sh` Test 8: outside git repo | Pass |
| All 11 real artifact types return correct next number | Cross-check: `find docs/<type>/` max vs script output for all types | Pass |

## Scope & Constraints

- The script lives in `skills/swain-design/scripts/next-artifact-number.sh`.
- No external dependencies beyond git and standard POSIX tools.
- Not a locking mechanism — it finds the current max. True collision prevention is handled by [SPEC-158](../(SPEC-158)-Artifact-Number-Collision-Detection/(SPEC-158)-Artifact-Number-Collision-Detection.md).
- Does not modify any files — pure read-only query.

## Implementation Approach

1. Parse and validate the TYPE argument.
2. Map TYPE to the docs subdirectory name (lowercase).
3. Collect all worktree paths from `git worktree list --porcelain`.
4. For each worktree, `find` matching artifact directories/files and extract numbers.
5. Use `git ls-tree` on trunk (or fallback branch) for the same directory to catch committed-but-not-checked-out artifacts.
6. Compute max, add 1, print.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | — | Agent-suggested decomposition of EPIC-043 |
| NeedsManualTest | 2026-03-23 | — | Implementation complete; 10/10 unit tests, 11/11 real-repo validation |
| Complete | 2026-03-23 | — | All 7 acceptance criteria verified with evidence |
