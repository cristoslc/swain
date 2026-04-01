---
title: "Worktree Entry Must Commit Staged Artifacts First"
artifact: SPEC-219
track: implementable
status: Complete
author: Cristos L-C
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Worktree Entry Must Commit Staged Artifacts First

## Problem Statement

Swain skills that create artifacts and then enter a worktree in the same session leave those artifacts stranded. A worktree is created from a git branch — it reflects committed history, not the working tree's uncommitted state. Any files created after the last commit (new specs, epics, ADRs, etc.) are absent in the worktree. The agent then operates on a stale snapshot, unaware of work it just did moments before.

## Desired Outcomes

An agent entering a worktree for implementation work always has access to every artifact it created in the same session. No artifact is silently dropped because it wasn't committed before the branch point.

## External Behavior

- Before creating a worktree (via `EnterWorktree`, `git worktree add`, or the worktree preamble in swain-do), the skill checks whether there are any uncommitted changes in the repository.
- If uncommitted changes exist, the skill stages and commits them before creating the worktree.
- The commit message follows the project's conventional-commit style and attributes the files accurately.
- After the commit, worktree creation proceeds normally.
- If there are no uncommitted changes, the check is a no-op.

## Acceptance Criteria

- **Given** a skill creates a new artifact file and immediately invokes the worktree preamble, **when** the worktree is created, **then** the artifact file is present and at the correct commit inside the worktree.
- **Given** no uncommitted changes exist, **when** the worktree preamble runs the pre-commit check, **then** it exits silently with no commit created.
- **Given** uncommitted changes include files from multiple operations (e.g., spec + ADR created together), **when** the pre-commit step runs, **then** all files are committed in a single commit before the worktree is created.
- **Given** the pre-commit commit fails (e.g., hook error), **when** the worktree preamble encounters the error, **then** it surfaces the error and halts — it does not create the worktree with missing files.

## Reproduction Steps

1. Run `/swain-design` to create a new SPEC artifact (file written to `docs/spec/Active/`).
2. In the same session, run `/swain-do` to begin implementation on that SPEC.
3. The swain-do worktree preamble creates a worktree from a new branch.
4. Inside the worktree, observe that the artifact file from step 1 is absent — it was never committed.

## Severity

high

## Expected vs. Actual Behavior

**Expected:** The artifact file created in step 1 is visible inside the worktree and present in `git log` of the new branch.

**Actual:** The artifact file is absent from the worktree. The worktree branch was cut before the file was committed, so it never entered the branch's history.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Artifact present in worktree | File exists at expected path inside worktree | — |
| No spurious commit when clean | `git log --oneline -1` hash unchanged after preamble on clean tree | — |
| Multi-file batch commit | Single commit contains all staged files | — |
| Hook failure halts worktree creation | Error surfaced; no worktree directory created | — |

## Scope & Constraints

- The fix applies to every swain skill that invokes the worktree preamble: primarily **swain-do** and **using-git-worktrees**.
- The pre-commit step must respect `.gitignore` — it should not accidentally stage ignored files.
- The fix must not bypass pre-commit hooks (`--no-verify` is prohibited per AGENTS.md conventions).
- Out of scope: detecting whether a file *should* have been created. The check is purely mechanical — stage and commit whatever is unstaged.

## Implementation Approach

1. Extract a reusable `ensure-committed.sh` helper (or inline the logic in each preamble) that:
   - Runs `git status --porcelain` and exits cleanly if output is empty.
   - Stages all untracked/modified files with `git add -A` (subject to `.gitignore`).
   - Commits with a conventional message: `chore: stage artifacts before worktree creation`.
2. Insert a call to this helper at the top of the worktree preamble in **swain-do** (before `git worktree add`).
3. Insert the same call in **using-git-worktrees** if it manages worktree creation independently.
4. Add a guard: if the commit fails, print the error and `exit 1` so the caller does not proceed to `git worktree add`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | 01eac4c | Initial creation |
| Complete | 2026-03-31 | 2f49e1f | All ACs verified; fix landed in skills/swain-do/SKILL.md |
