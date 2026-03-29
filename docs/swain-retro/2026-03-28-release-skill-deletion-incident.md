---
title: "Retro: v0.21.0-alpha release deleted all skill files"
artifact: RETRO-2026-03-28-release-skill-deletion
track: standing
status: Active
created: 2026-03-28
last-updated: 2026-03-28
scope: "Incident where a dispatched release agent deleted all skills/swain-* files from the working tree"
period: "2026-03-28 23:05 — 2026-03-28 23:07 EDT"
linked-artifacts:
  - swain-release
  - swain-sync
---

# Retro: v0.21.0-alpha release deleted all skill files

## Summary

A dispatched agent running swain-release from a worktree caused all 14 `skills/swain-*` directories (100+ tracked files) to be deleted from the main worktree's working tree. The files remained in HEAD (tracked by git) but were absent on disk, breaking all `.claude/skills/` symlinks and rendering every swain skill unavailable.

The operator discovered the issue when `/swain-session` returned "Unknown skill." Files were restored via `git checkout HEAD -- skills/swain-*/`.

## Timeline

| Time (EDT) | Event |
|------------|-------|
| 23:05:46 | Agent commits `release: v0.21.0-alpha` on **trunk** (wrong branch) |
| 23:06:00 | Agent switches to release, commits again, switches back to trunk |
| 23:06:29 | Agent starts rebase onto origin/trunk |
| 23:06:44 | Rebase aborted |
| 23:06:53 | `git reset HEAD~1` — undo release commit on trunk |
| 23:07:08 | `git reset HEAD` (likely `--hard`) — clean working tree; **skills deleted here** |
| 23:07:08 | Rapid branch switching, re-commit on release and trunk |
| 23:07:31 | v0.21.0-alpha finally committed on release (72a5822) |
| ~23:18 | v0.21.1-alpha released (388e6ac) — skills already missing, unnoticed |
| ~23:41 | Operator discovers broken skills in new session |

14 reflog entries in 2 minutes — the agent was thrashing through recovery attempts.

## Root cause

The dispatched agent was in a **worktree** but swain-release requires operating on **trunk** and **release** branches directly. The agent navigated to the main worktree to perform branch operations, then thrashed through rebase, abort, and reset cycles when its first commit landed on the wrong branch. A `git reset --hard HEAD` during recovery deleted tracked files from the working tree.

The `!skills/swain-*/` force-tracking pattern in `.gitignore` (negated ignore for tracked directories) may interact poorly with `reset --hard` when combined with rapid branch switching.

## Contributing factors

1. **Worktree was wrong isolation for release** — the agent was dispatched into a worktree, but release inherently needs multi-branch access. This forced the agent to operate on the main worktree anyway, adding confusion about which HEAD and working tree it was modifying.

2. **No guardrails against destructive recovery** — the release skill has no prohibition against `reset --hard`, `rebase`, or other working-tree-destructive operations. The agent chose these freely when trying to recover from its initial mistake.

3. **No forensic trail** — `.agents/session.json` stores JSON state (bookmark, focus lane), not the commands the agent ran. When a dispatched agent causes damage, there is no audit trail to reconstruct exactly what happened. The reflog was the only evidence, and it doesn't distinguish `reset` from `reset --hard`.

4. **Silent failure** — the skill deletion was not detected until the operator started a new session. No health check, hook, or guard noticed that 100+ tracked files had vanished.

## Reflection

### What went well

- Git's tracked-file safety net worked: `git checkout HEAD --` restored everything
- The reflog provided enough forensic data to reconstruct the timeline
- The operator noticed quickly (within ~30 minutes)

### What was surprising

- A dispatched agent can silently destroy the main worktree's state while operating from a worktree branch — worktree isolation is not a safety boundary for multi-branch operations
- `reset --hard` can delete force-tracked files (those with `!` gitignore negation) without staging the deletion, making the loss invisible to `git diff --cached`

### What would change

1. **swain-release should detect worktree context and refuse to run** — prompt the operator to run from trunk instead
2. **Generalize: skills should declare their branch requirements** — release and sync need trunk access; design and do work fine in worktrees. A skill that needs trunk should be able to say so.
3. **Ban destructive git operations in dispatched agents** — `reset --hard`, `clean -f`, `checkout .` should never appear in skill instructions. Recovery should use `stash`, `merge --abort`, or operator escalation.
4. **Add a preflight or post-flight check** — swain-doctor or a hook should verify that `skills/swain-*` files exist on disk, not just in the index.

### Patterns observed

This is the second release-related incident (see also the chaotic v0.21.0-alpha release needing 4 attempts). The release skill's multi-branch design is a recurring source of complexity. The worktree dispatch model assumes operations are branch-local, but release is inherently cross-branch.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_release_no_worktree.md | feedback | Release and multi-branch operations must refuse worktree isolation |
| feedback_retro_no_destructive_recovery.md | feedback | Dispatched agents must not use reset --hard or other destructive recovery |

## SPEC candidates

These need skill/design changes, not memory:

1. **Session log forensics** — `.agents/session.json` stores state only; dispatched agents need a command-level JSONL event stream for audit. Currently session logs from worktrees may be discarded on merge rather than merged to trunk.
2. **Worktree-inappropriate operation detection** — skills that require multi-branch access (release, sync-to-release) should declare this requirement so the dispatch system can route them to trunk instead of a worktree.
3. **Skill file health check** — swain-doctor should verify `skills/swain-*` files exist on disk (not just in the index) as a preflight/post-flight check.
