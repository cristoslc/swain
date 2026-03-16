---
title: "swain-sync: worktree-aware execution"
artifact: SPEC-039
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-015
linked-artifacts:
  - ADR-005
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# swain-sync: worktree-aware execution

## Problem Statement

When an agent runs swain-sync from inside a git worktree (e.g., `.claude/worktrees/agent-abc123`), three distinct failure modes occur:

1. **Bookmark script not found.** The bookmark command `find . .claude .agents -path '*/swain-bookmark.sh' ...` searches relative to the worktree root, which does not contain `.claude/` or `.agents/`. The script is only present in the main worktree (repo root), so the bookmark silently no-ops.

2. **Stash collisions.** `git stash` is global across all worktrees in a repo. An auto-stash from one worktree can interleave with stashes from another, producing confusing pop-order conflicts and unrelated changes surfacing in unexpected worktrees.

3. **Rebase against a non-existent remote branch, then wrong push target.** Worktree branches (e.g., `worktree-agent-abc123`) typically have no remote tracking counterpart. The Step 1 rebase command `git rebase origin/<branch>` fails with "fatal: needed a single revision". More fundamentally, pushing the worktree branch to a remote would create an orphaned remote branch — worktree work is meant to land on `main`, not persist as its own remote branch.

## External Behavior

**Inputs:** swain-sync is invoked by an agent running in any directory within a git repository (main worktree or linked worktree).

**Detection:** The skill determines the worktree context at startup using `git rev-parse --git-common-dir` — if the result differs from `git rev-parse --git-dir`, the agent is in a linked worktree.

**Outputs / Postconditions:**

- Changes committed in the worktree and merged into `main` (fast-forward via `git push origin HEAD:main`).
- Session bookmark always updated (whether in main or linked worktree).
- No cross-worktree stash contamination.
- No orphaned remote worktree branches.
- Clear error messaging when merge is not possible (e.g., diverged history, no remote configured).

**Constraints:**

- Must not change behavior for agents running in the main worktree.
- Must not force-push or discard local changes.
- Must remain a single SKILL.md prose file — no shell script extraction unless a follow-on spec justifies it.

## Acceptance Criteria

**AC-1: Worktree detection**
- Given: An agent invokes swain-sync from a linked worktree directory.
- When: Step 1 begins.
- Then: The skill detects the worktree context using `git rev-parse --git-common-dir` vs `git rev-parse --git-dir` and sets a `IN_WORKTREE` flag for use in later steps.

**AC-2: Bookmark script discovery uses repo root**
- Given: An agent is in a linked worktree.
- When: The session bookmark step executes.
- Then: The `find` command roots its search at the main worktree root (obtained via `git rev-parse --show-toplevel` from the common-dir path) rather than `.`, so `.claude/skills/swain-session/scripts/swain-bookmark.sh` is reliably found.

**AC-3: Stash is scoped to worktree**
- Given: An agent in a linked worktree has uncommitted local changes before rebase.
- When: The auto-stash is created.
- Then: The stash message includes the worktree name (e.g., `swain-sync: auto-stash [worktree-agent-abc123]`) so the stash is identifiable if manual recovery is needed. No other behavioral change — the stash/pop sequence is otherwise identical.

**AC-4: Remote branch absent → rebase onto origin/main instead**
- Given: An agent is in a linked worktree whose branch has no remote tracking counterpart.
- When: Step 1 runs `git rev-parse --abbrev-ref --symbolic-full-name @{u}`.
- Then: If the command returns an error (no upstream), the skill fetches `origin` and rebases the worktree branch onto `origin/main` (so the commits apply cleanly as a fast-forward). If `origin/main` cannot be fetched, skip fetch/rebase and proceed to Step 2.

**AC-5: Worktree changes land on main via fast-forward push**
- Given: An agent is in a linked worktree and has committed changes.
- When: Step 6 pushes.
- Then: The skill pushes using `git push origin HEAD:main` — landing the worktree's commits directly on `main` without creating a remote worktree branch. If the push is rejected (non-fast-forward), report the conflict and stop; do not force-push.

**AC-6: Branch protection detected → open PR instead of pushing**
- Given: An agent is in a linked worktree and `git push origin HEAD:main` is rejected with a message referencing branch protection or required reviews.
- When: Step 6 handles the push rejection.
- Then: The skill runs `gh pr create --base main --head <worktree-branch> --title <commit-subject> --body <commit-body>` and reports the PR URL. It does not retry the push. Worktree pruning (AC-7) still runs after PR creation.

**AC-7: Worktree is pruned after landing**
- Given: An agent in a linked worktree has successfully pushed to main (AC-5) or opened a PR (AC-6).
- When: The push or PR creation completes.
- Then: The skill removes the worktree (`git worktree remove --force <worktree-path>` from `REPO_ROOT`) and runs `git worktree prune`. The worktree path is resolved from `git worktree list` by matching the current working directory.

**AC-8: Main worktree behavior unchanged**
- Given: An agent is in the main worktree (not a linked worktree).
- When: Any step of swain-sync executes.
- Then: Behavior is identical to swain-sync v1.1.0 — no regressions. Worktree-specific steps (AC-4 through AC-7) are skipped entirely.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1: Worktree detection | | |
| AC-2: Bookmark script discovery | | |
| AC-3: Stash scoped to worktree | | |
| AC-4: Rebase onto origin/main when remote branch absent | | |
| AC-5: Push lands on main via HEAD:main | | |
| AC-6: Branch protection → PR created | | |
| AC-7: Worktree pruned after land | | |
| AC-8: Main worktree unchanged | | |

## Scope & Constraints

**In scope:**
- SKILL.md prose changes to detect worktree context and adapt Steps 1, 6, and the bookmark step.
- Stash message scoping (label only — no behavioral change to stash/pop).
- PR creation fallback when branch protection blocks direct push.
- Worktree pruning after successful land.

**Out of scope:**
- Pushing to a remote that doesn't exist (no remote configured at all) — environment misconfiguration, not a worktree problem. Report and stop.
- Worktree creation — handled by Claude Code, `using-git-worktrees`, swain-dispatch, or swain-do. See ADR-005.
- Extracting swain-sync logic into shell scripts — separate concern, separate spec if desired.

## Implementation Approach

The change is purely prose in `skills/swain-sync/SKILL.md`. No new files.

**Step 1 prefix** — add worktree detection:
```bash
GIT_COMMON=$(git rev-parse --git-common-dir)
GIT_DIR=$(git rev-parse --git-dir)
IN_WORKTREE=$( [ "$GIT_COMMON" != "$GIT_DIR" ] && echo "yes" || echo "no" )
REPO_ROOT=$(git rev-parse --show-toplevel)
```

**Step 1 body** — when `IN_WORKTREE=yes` and `@{u}` is absent, rebase onto `origin/main` instead of the worktree's own remote branch:
```bash
git fetch origin
git rebase origin/main
```
If `@{u}` exists (unusual but possible for worktrees), use the existing upstream rebase path unchanged.

**Step 3 stash message** — append branch name so worktree stashes are identifiable:
```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git stash push -m "swain-sync: auto-stash [$BRANCH]"
```

**Step 6** — when `IN_WORKTREE=yes`, push to `main` on remote rather than creating a remote worktree branch:
```bash
git push origin HEAD:main
```
If rejected (non-fast-forward), report and stop — do not retry with `--force`.

When `IN_WORKTREE=no`, keep the existing `git push` / `git push -u origin HEAD` behavior unchanged.

**Bookmark step** — replace `find . .claude .agents` with:
```bash
find "$REPO_ROOT" -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null
```

TDD cycles:
1. RED: test that bookmark `find` returns a path when called from a worktree → GREEN: fix `find` to use `$REPO_ROOT`
2. RED: test that Step 1 rebases onto `origin/main` (not a missing remote branch) when `@{u}` absent → GREEN: add worktree rebase guard
3. RED: test that Step 6 uses `HEAD:main` when `IN_WORKTREE=yes` → GREEN: add worktree push path
4. RED: test that a branch-protection rejection triggers `gh pr create` → GREEN: add rejection-message detection and PR fallback
5. RED: test that worktree directory is removed after successful land → GREEN: add `git worktree remove` + `git worktree prune` step

See ADR-005 for the full workflow rationale.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation |
| Ready | 2026-03-14 | d4a991c | Approved for implementation |
| Complete | 2026-03-14 | dacbf2c | Implemented in EPIC-015 Active transition; all AC criteria met |
