---
title: "Retro: ADR-034 Worktree Location Standardization"
artifact: RETRO-2026-04-05-adr-034-worktree-standardization
track: standing
status: Active
created: 2026-04-05
last-updated: 2026-04-05
scope: "ADR-034 — drop .claude/worktrees/ fallback, standardize on .worktrees/"
period: "2026-04-05 — 2026-04-05"
linked-artifacts:
  - ADR-034
  - ADR-033
  - EPIC-056
---

# Retro: ADR-034 Worktree Location Standardization

## Summary

Single-session ADR + implementation that removed the `.claude/worktrees/` fallback from `bin/swain` and aligned all references across the codebase. Net result: `choose_worktree_parent()` dropped from 14 lines to 3, one gitignore entry removed, stale permissions cleaned, skill docs and test fixtures updated. Detection scripts kept `.claude/worktrees/` as a flagged bad-path pattern — turning former production code into a safety net.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [ADR-034](../adr/Active/(ADR-034)-Standardize-Worktree-Location.md) | Standardize Worktree Location to .worktrees/ | Created (Active) |

## Reflection

### What went well

Tight scope made this a clean single-pass change. The exploration phase found every reference in one sweep — no surprises during implementation. The grep-based verification at the end confirmed zero residual references in modifiable files.

The decision to keep `.claude/worktrees/` in detection scripts (`detect-worktree-links.sh`) was the right nuance — it turns a former "path we might create" into "path that is always wrong," making the safety net strictly more useful post-migration.

### What was surprising

The commit agent picked up additional changes beyond the plan (AGENTS.md condensation, index rebuilds, symlink cleanup). This is the recurring pattern where dispatched agents expand scope beyond their brief. The extra changes were benign here but worth noting.

### What would change

The ADR was initially written on trunk then manually copied to the worktree — a minor workflow friction. The ideal flow is: create worktree first, write everything there. The initial trunk write was an artifact of the plan mode constraint (read-only until plan approval).

### Patterns observed

This is the third worktree-infrastructure simplification in rapid succession: [EPIC-056](../epic/Complete/(EPIC-056)-Worktree-Isolation-Redesign/(EPIC-056)-Worktree-Isolation-Redesign.md) (full redesign), [ADR-033](../adr/Active/(ADR-033)-Born-in-Worktree-Session-Isolation.md) (born-in-worktree model), now ADR-034 (path standardization). Each one removed complexity left over from the previous iteration. The pattern suggests a healthy convergence — each pass tightens the model, and the remaining surface area for future simplification is shrinking.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Dispatched agents expand scope | SPEC candidate | Commit agents should have explicit exclusion lists for files outside the change set (echoes existing feedback memory `feedback_retro_agent_exclusion_criteria.md`) |
| Plan-mode artifacts land on trunk | Process observation | ADR created on trunk during plan mode, then manually copied to worktree — minor friction, not worth a spec |
