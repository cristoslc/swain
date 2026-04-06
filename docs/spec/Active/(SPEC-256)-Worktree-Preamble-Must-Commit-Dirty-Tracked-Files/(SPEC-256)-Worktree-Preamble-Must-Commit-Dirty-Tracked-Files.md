---
title: "Worktree preamble must commit dirty tracked files before branching"
artifact: SPEC-256
track: implementable
status: Active
author: Cristos L-C
created: 2026-04-03
last-updated: 2026-04-03
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-002
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree preamble must commit dirty tracked files before branching

## Problem Statement

The swain-do worktree isolation preamble only commits untracked files before creating a worktree. It skips modified tracked files, claiming they "are already in history and appear in the worktree regardless." This is incorrect — a new worktree checks out from HEAD, so any uncommitted modifications to tracked files are invisible inside the worktree.

## Desired Outcomes

Agents working in worktrees see the same file state the operator saw on trunk at the moment work was dispatched. No silent data loss from uncommitted edits.

## External Behavior

**Before worktree creation**, the preamble:
1. Detects both untracked files and modified tracked files.
2. Stages and commits all of them in a single `chore:` commit.
3. Creates the worktree from the updated HEAD.

If the commit fails (e.g., pre-commit hook rejection), the preamble stops and surfaces the error — same as the current untracked-only path.

## Acceptance Criteria

- **Given** modified tracked files exist in the working tree, **when** the worktree preamble runs, **then** those modifications are committed before the worktree branch is created.
- **Given** both untracked and modified tracked files exist, **when** the preamble runs, **then** a single commit captures all of them.
- **Given** no untracked or modified files exist, **when** the preamble runs, **then** no commit is created and worktree creation proceeds normally.
- **Given** the commit fails, **when** the preamble runs, **then** worktree creation is aborted and the error is surfaced.

## Reproduction Steps

1. On trunk, modify a tracked file (e.g., edit an existing SPEC's frontmatter).
2. Invoke swain-do on a different SPEC that triggers worktree creation.
3. Inside the new worktree, check the modified file — it shows the old committed content, not the trunk working-tree edits.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** The worktree contains the operator's in-progress edits to tracked files, because the preamble committed them before branching.

**Actual:** The worktree shows the last-committed state of tracked files. Modifications made on trunk before worktree creation are silently lost from the agent's perspective.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The fix is a skill-file edit to `swain-do/SKILL.md` — specifically the worktree isolation preamble section.
- The false claim about modified tracked files must be corrected in the prose.
- The bash snippet must be updated to detect and stage both `--others` (untracked) and modified tracked files.
- No script changes needed — this is entirely within the skill's behavioral guidance.

## Implementation Approach

1. Update the preamble's step 1 bash snippet to also detect modified tracked files (`git diff --name-only`).
2. Stage both untracked and modified files before committing.
3. Correct the prose that claims modified tracked files don't need committing.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-03 | — | Initial creation |
