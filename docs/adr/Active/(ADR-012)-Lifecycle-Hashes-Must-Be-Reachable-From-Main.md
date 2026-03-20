---
title: "Lifecycle Hashes Must Be Reachable From Main"
artifact: ADR-012
track: standing
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
linked-artifacts:
  - ADR-011
  - SPIKE-022
depends-on-artifacts: []
---

# Lifecycle Hashes Must Be Reachable From Main

## Context

Every swain artifact embeds a lifecycle table that records phase transitions with commit hashes. These hashes are used for audit trails, traceability, and cross-artifact references. The invariant has been in place since the project's early lifecycle format design.

The invariant: **every commit hash recorded in a lifecycle table must be reachable from main via `git log`.** Any git operation that orphans, rewrites, or removes commits referenced in lifecycle tables breaks artifact traceability.

This was surfaced explicitly during [ADR-011](../Proposed/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md) discussion (worktree landing strategy) when squash-merge was evaluated and rejected — squash-merge orphans the agent's commits, making lifecycle hashes point to unreachable commits after worktree pruning.

## Decision

Lifecycle commit hashes must be reachable from main. This constrains all git workflow decisions:

- **No squash-merge** for worktree landing — orphans the original commits
- **No force-push to main** — rewrites history, potentially removing stamped commits
- **No rebase of commits already stamped in lifecycle tables** — rewrites hashes
- **Branch pruning is safe** only when all stamped commits are reachable from main (merge-based landing ensures this; rebase-based landing also ensures this as long as the rebase succeeds)
- **No `git filter-branch` or history rewriting on main**

The two-commit stamping pattern (lifecycle-format.md) exists specifically to satisfy this invariant: commit A records the transition, commit B stamps A's hash. Both commits are on the same branch that eventually reaches main.

## Alternatives Considered

**Content-addressed stamps (hash of file content instead of commit hash):**
Rejected — loses the git-native traceability. You can't `git show` a content hash to see what changed.

**No stamps (track phases only by directory location):**
Rejected — directory location shows current phase but not transition history. The lifecycle table records *when* each transition happened and *what commit* caused it.

**Store hashes but accept they may become unreachable:**
Rejected — an unreachable hash is useless for auditing. If the hash can't be resolved, the lifecycle table is decorative, not functional.

## Consequences

**Positive:**
- `git log` and `git show` work on any lifecycle hash — full traceability
- Auditing tools can walk lifecycle tables and verify each transition
- Cross-artifact references via commit hash are stable

**Constraints imposed:**
- Landing strategy must use merge (not squash) to keep agent commits on main
- Force-push to main is prohibited
- History rewriting tools are prohibited on main
- Any future git workflow ADR must be evaluated against this invariant

## Linked Artifacts

- [ADR-011](../Proposed/(ADR-011)-Worktree-Landing-Via-Merge-With-Retry.md) — depends on this; merge-based landing preserves reachability
- [SPIKE-022](../../research/Active/(SPIKE-022)-Multi-Agent-Collision-Vectors/(SPIKE-022)-Multi-Agent-Collision-Vectors.md) — investigated collision vectors; squash-merge rejected due to this invariant

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Codified from established practice; invariant since project inception |
