---
title: "Worktree Lifecycle: swain-do Creates, swain-sync Lands"
artifact: ADR-005
track: standing
status: Superseded
superseded-by: ADR-011
author: cristos
created: 2026-03-14
last-updated: 2026-03-20
linked-artifacts:
  - SPEC-039
depends-on-artifacts: []
trove: ""
---

# Worktree Lifecycle: swain-do Creates, swain-sync Lands

## Context

Swain agents are increasingly dispatched into git worktrees for isolated task execution — whether created by Claude Code's native worktree support, the `using-git-worktrees` superpowers skill, swain-dispatch, or manual operator setup. When an agent in a worktree invokes swain-sync, several questions arise:

1. **What does sync mean in a worktree context?** Mid-task commits are managed by the agent independently. swain-sync is invoked only at task completion — it is the "land and clean up" step, not a general-purpose commit helper.

2. **Where should the changes land?** A worktree branch is an ephemeral isolation mechanism, not a persistent feature branch. Work should land on `main`, not on a remote copy of the worktree branch.

3. **How should landing be attempted?** Repos may have branch protection rules requiring PR review before changes reach `main`. swain-sync must detect this and respond correctly rather than silently failing or bypassing the gate.

4. **What should happen to the worktree afterward?** Once work has landed (or a PR has been opened), the local worktree directory has no further purpose and should be removed.

5. **Does swain-sync care how the worktree was created?** No. Worktrees may be created by swain-do (the standard path), Claude Code natively, or a human operator. swain-sync detects worktree state from git itself and does not depend on provenance.

6. **Who is responsible for ensuring work happens inside a worktree?** swain-do. It checks on every invocation and creates a worktree via `using-git-worktrees` if one doesn't exist. This ensures isolation is enforced at the point of task dispatch, not left to chance.

## Decision

**swain-sync in a linked worktree follows a fixed completion workflow:**

### 1. Detect worktree context at startup

Use `git rev-parse --git-common-dir` vs `git rev-parse --git-dir`. If they differ, the agent is in a linked worktree. Capture `REPO_ROOT` (the main worktree root) for use in bookmark lookup and worktree pruning.

### 2. Rebase onto origin/main (not the worktree branch's upstream)

Worktree branches typically have no remote counterpart. Instead of trying to fetch/rebase from a non-existent `origin/<worktree-branch>`, fetch `origin` and rebase onto `origin/main`. This ensures the worktree's commits apply as a clean fast-forward when they land on `main`.

If the rebase produces conflicts, abort and report — do not push.

### 3. Land on main

Attempt `git push origin HEAD:main`.

- **Fast-forward succeeds:** done, proceed to cleanup.
- **Rejected (non-fast-forward):** main has diverged since the rebase — report and stop. Do not force-push.
- **Rejected (branch protection):** detected when the rejection message references branch protection or required reviews. In this case, create a PR targeting `main` using `gh pr create` and stop. The operator merges when ready.

### 4. Prune the worktree

After a successful push or PR creation, remove the worktree:

```bash
cd "$REPO_ROOT"
git worktree remove --force "<worktree-path>"
git worktree prune
```

The worktree path is obtained from `git worktree list` — match on the current working directory.

### 5. Worktree creation is owned by swain-do

swain-do checks the current git context on every invocation using `git rev-parse --git-common-dir` vs `git rev-parse --git-dir`. If the agent is already in a linked worktree, it proceeds normally. If not, swain-do invokes the `using-git-worktrees` superpowers skill to create a worktree before handing off for implementation or execution.

If worktree creation fails for any reason (superpowers not installed, git error, disk issue), swain-do stops and reports the failure to the operator — it does not fall back to running in the main worktree. Isolation is not optional.

swain-sync does not create worktrees.

## Alternatives Considered

**Push worktree branch to remote, let operator merge.**
Rejected: creates orphaned remote branches, requires manual cleanup, and leaves the work stranded. Agents should complete the full landing, not hand off half-finished state.

**Always open a PR (even without branch protection).**
Rejected: adds unnecessary friction on unprotected repos (the common case for personal/internal projects). Direct fast-forward push is appropriate when the gate allows it.

**Skip pruning — leave worktree cleanup to the operator.**
Rejected: worktree directories accumulate and confuse future git operations (e.g., `git worktree list` shows stale entries). Since swain-sync marks task completion, it is the natural cleanup point.

**swain-sync creates its own worktrees.**
Rejected: sync is not a dispatch mechanism. Worktree creation belongs upstream (at task start, via swain-do), not at task completion.

**Fall back to main worktree if worktree creation fails.**
Rejected: isolation is the point. Running implementation tasks in the main worktree risks polluting in-progress state and makes concurrent agent dispatch unsafe. Failure must be surfaced, not silently degraded.

## Consequences

**Positive:**
- Agents fully complete tasks — land, clean up, and leave the repo in a clean state.
- Repos with PR requirements are handled correctly; direct-push repos get lower friction.
- No orphaned remote worktree branches.
- Worktree provenance (who created it) is irrelevant — swain-sync works uniformly.
- Isolation is guaranteed at dispatch time: swain-do ensures every implementation runs in a worktree, regardless of how the agent was invoked.
- Worktree creation is centralized in one skill (`using-git-worktrees` via swain-do), not scattered across swain-dispatch, Claude Code, and manual setup.

**Accepted downsides:**
- swain-do requires `using-git-worktrees` (superpowers) to be installed. If superpowers is absent, swain-do cannot proceed with implementation tasks and must stop. Operators must install superpowers to use swain-do for implementation dispatch.
- A PR-required repo always leaves the agent waiting for human merge — agent cannot complete autonomously. This is intentional: branch protection expresses operator intent.
- `git push origin HEAD:main` bypasses commit signing if the agent's git config uses a per-worktree signing key that isn't recognized by the remote. Operators using commit signing should ensure keys are configured at the repo level, not the worktree level.
- Worktree pruning with `--force` discards any uncommitted changes in the worktree at cleanup time. Since swain-sync requires a clean working tree before pushing, this should never lose data — but if the worktree is in an unexpected state, `--force` could silently discard work. This risk is accepted.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-14 | — | Approved during SPEC-039 design review |
| Superseded | 2026-03-20 | -- | Superseded by ADR-011 |
