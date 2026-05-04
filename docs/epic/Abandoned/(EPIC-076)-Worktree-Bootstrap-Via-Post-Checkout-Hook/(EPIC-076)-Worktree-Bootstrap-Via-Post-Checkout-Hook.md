---
title: "Worktree Bootstrap via Post-Checkout Hook"
artifact: EPIC-076
track: container
status: Abandoned
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
parent-initiative: INITIATIVE-017
priority-weight: high
success-criteria:
  - A tracked post-checkout hook symlinks all gitignored runtime dirs into every worktree automatically after `git worktree add`
  - `core.hooksPath` is set via a deterministic, idempotent install script that chains existing hooks instead of overwriting them
  - bin/swain `create_session_worktree()` no longer performs inline symlinking — all bootstrap logic lives in the hook
  - using-git-worktrees skill defers entirely to the hook and documents the dependency
  - swain-doctor's symlink repair is a safety net only, not the primary mechanism
  - The hook is fast (runs on every checkout) and idempotent (re-runs safely without side effects)
depends-on-artifacts:
  - ADR-040
addresses: []
evidence-pool: ""
---

# Worktree Bootstrap via Post-Checkout Hook

## Goal / Objective

Make a tracked `post-checkout` hook the only place that symlinks gitignored runtime dirs into worktrees. This implements [ADR-040](../../../adr/Superseded/(ADR-040)-Worktree-Bootstrap-Via-Post-Checkout-Hook.md). Every entry point — `bin/swain`, skill scripts, and bare `git worktree add` — must defer to the hook. No more inline symlinking.

## Desired Outcomes

Any agent launched in a worktree sees the same skill trees, runtime state, and peer-agent config as trunk. No entry point needs to know the symlink ritual. The operator never hits a "broken worktree" where skills fail or onboarding re-runs. Swain-doctor's repair pass becomes a safety net for old worktrees only.

## Progress

<!-- Auto-populated from session digests. -->

## Scope Boundaries

**In scope:**
- Tracked post-checkout hook script that symlinks gitignored runtime dirs into worktrees
- Deterministic, idempotent install script for the hook and `core.hooksPath` with chaining support
- Rewriting `bin/swain` `create_session_worktree()` to remove inline symlinking
- Rewriting `using-git-worktrees` skill to defer to the hook
- Downgrading `swain-doctor` symlink repair to safety-net status
- The shared-dir list data source (what gets symlinked and from where)

**Out of scope:**
- [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md) `.agents/` to `.swain/` migration (separate EPIC)
- Windows/symlink-hostile platform fallback (portability track)
- The `specwatch` / `design-check` / `adr-check` hooks (already in `scripts/hooks/`, unrelated to worktree bootstrap)
- Skill content changes beyond the worktree-adjacent skills listed above

## Child Specs

- **SPEC-307**: Idempotent hook install script. Installs the post-checkout hook into a tracked directory. Sets `core.hooksPath`. Chains any pre-existing hooks config instead of overwriting it.
- **SPEC-308**: Tracked post-checkout hook. Reads the shared-dir list. Walks each entry in the common root. Creates missing symlinks in the current worktree. Fast and idempotent.
- **SPEC-309**: Remove inline symlinking from `bin/swain` `create_session_worktree()`. The function stops creating skill dir, `.swain-init`, and `agent_dirs` symlinks. The hook handles them.
- **SPEC-310**: Rewrite `using-git-worktrees` skill to defer to the hook. Remove any inline symlinking steps. Document the hook dependency.
- **SPEC-311**: Downgrade `swain-doctor` symlink repair to safety net. Shrink check 12 and SPEC-290 repair to only fix pre-hook worktrees and stale links. Add a deprecation note.

## Key Dependencies

- [ADR-040](../../../adr/Superseded/(ADR-040)-Worktree-Bootstrap-Via-Post-Checkout-Hook.md) must stay Active. It is the decision this EPIC implements.
- [SPEC-290](../../../spec/Active/(SPEC-290)-swain-init-not-symlinked-into-pre-existing-worktrees/(SPEC-290)-swain-init-not-symlinked-into-pre-existing-worktrees.md) will be partially superseded. The repair pass stays but narrows in scope.
- [ADR-041](../../../adr/Active/(ADR-041)-Swain-Runtime-State-Location.md) changes the hook's directory target (`.agents/` to `.swain/`). That is a separate EPIC. This one writes code against `.agents/` paths and plans for the later migration.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Initial creation |
| Abandoned | 2026-04-13 | — | Superseded by ADR-042. Tracking all runtime and peer-agent dirs removes the need for a post-checkout hook. |