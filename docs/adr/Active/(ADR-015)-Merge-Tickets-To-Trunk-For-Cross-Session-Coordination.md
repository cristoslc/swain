---
title: "Merge Tickets To Trunk For Cross-Session Coordination"
artifact: ADR-015
track: standing
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-25
linked-artifacts:
  - INITIATIVE-013
  - EPIC-043
  - SPIKE-043
  - SPEC-165
depends-on-artifacts: []
evidence-pool: ""
---

# Merge Tickets To Trunk For Cross-Session Coordination

## Context

Swain uses `tk` (ticket) for execution tracking during SPEC implementation. Tickets live in `.tickets/` as markdown files with YAML frontmatter. They track task status, dependencies, notes, and claims — all the state an agent needs to resume work mid-session or across sessions.

The original ADR-015 (2026-03-23) declared tickets ephemeral — not committed to trunk, discarded with the worktree. This was adopted to solve worktree cleanup friction, retro quality, and stale ticket noise.

Within 24 hours, the decision caused data loss: an agent used `ExitWorktree` with `discard_changes: true` (to discard "just tickets"), which also silently discarded unmerged implementation commits on the worktree branch. The root cause: `discard_changes: true` is a blunt instrument that discards *all* uncommitted state, and the "tickets are ephemeral" framing encouraged its use without checking for unmerged work.

Additionally, the ephemeral model forecloses a valuable coordination primitive: **collision detection between parallel agents.** If tickets are committed, two agents claiming the same ticket would produce a merge conflict — surfacing the collision at exactly the right moment. Uncommitted tickets are invisible across worktrees, so parallel agents can unknowingly duplicate work.

## Decision

**Tickets are committed coordination state.** They are committed in worktree branches, merge to trunk with the rest of the work, and cleaned up when the parent SPEC reaches a terminal state.

Specific rules:

1. **Tickets are committed in worktree branches.** Before exiting a worktree, commit `.tickets/` files along with the rest of the work. This ensures `ExitWorktree` with `discard_changes: false` works cleanly — no uncommitted files, no unmerged commits silently lost.
2. **Tickets merge to trunk.** When a worktree branch merges, tickets land on trunk. This makes them visible to all agents: `tk ready` shows in-progress work across the project, `tk claim` locks are visible, and duplicate work is surfaced via merge conflicts.
3. **Tickets are cleaned up on SPEC terminal transition.** When swain-do's plan completion handoff transitions a SPEC to Complete or Abandoned, delete the closed tickets in the same commit. This keeps trunk clean without manual intervention.
4. **`ExitWorktree` uses `discard_changes: false` by default.** Never use `discard_changes: true` as a shortcut to skip ticket cleanup. If ExitWorktree refuses due to uncommitted files, commit them first. The refusal is a safety net, not friction.
5. **Retros still use session logs, not tickets.** This part of the original decision stands — tickets record *what tasks existed*, session logs record *what happened*. Retros need the narrative.
6. **`.tickets/` is NOT in `.gitignore`.** Remove it if present.

## Alternatives Considered

**A. Keep tickets ephemeral (original ADR-015).** Rejected — caused data loss within 24 hours via `discard_changes: true`, and forecloses cross-agent coordination.

**B. PreToolUse hook on ExitWorktree to prevent data loss.** Considered — a hook could check for unmerged commits before allowing removal. This solves the data loss problem but not the coordination problem. Tickets would remain invisible across worktrees.

**C. Commit tickets but gitignore on trunk.** Rejected — defeats the purpose. Tickets need to be visible on trunk for cross-agent coordination to work.

## Consequences

**Positive:**
- **No more data loss from ExitWorktree.** `discard_changes: false` is the safe default; committed tickets don't trigger refusal.
- **Cross-agent collision detection.** Merge conflicts on claimed tickets surface parallel work on the same SPEC before it wastes effort.
- **Cross-session resumability.** A new session on trunk can see in-progress tickets from prior sessions via `tk ready` — no signal scanning heuristics needed.
- **`tk ready` becomes a project-wide coordination primitive.** Claimed and open tickets on trunk are visible to all agents.

**Negative:**
- **Tickets accumulate on trunk between SPEC completions.** Mitigation: the cleanup-on-terminal-transition rule keeps this bounded. Between SPEC start and SPEC end, a handful of ticket files exist — typically 5-15 small markdown files per SPEC.
- **Merge conflicts on tickets require resolution.** Mitigation: ticket merge conflicts are the *point* — they surface coordination failures. Resolution is straightforward: the agent whose claim was second defers to the first.

**Downstream changes required:**
- **swain-do SKILL.md**: Update ticket lifecycle section to reflect committed state. Update plan completion handoff to delete closed tickets on SPEC terminal transition. Update worktree exit to commit tickets before calling ExitWorktree, use `discard_changes: false`.
- **.gitignore**: Remove `.tickets/` entry if present.
- **swain-sync SKILL.md**: Include `.tickets/` in staged files during commit.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-23 | — | Original: tickets as ephemeral scaffolding |
| Active (amended) | 2026-03-25 | -- | Reversed: tickets as committed coordination state. Triggered by data loss from ExitWorktree discard and need for cross-agent collision detection. |
