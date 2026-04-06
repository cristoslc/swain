---
title: "Standardize Worktree Location to .worktrees/"
artifact: ADR-034
track: standing
status: Active
author: Cristos L-C
created: 2026-04-05
last-updated: 2026-04-05
linked-artifacts:
  - ADR-033
  - EPIC-056
  - ADR-011
depends-on-artifacts: []
evidence-pool: ""
---

# Standardize Worktree Location to .worktrees/

## Context

`bin/swain`'s `choose_worktree_parent()` function uses a dual-path strategy: prefer `.worktrees/`, fall back to `.claude/worktrees/`. The fallback exists because early versions of swain ran inside Claude Code, which stored worktrees under `.claude/`. Now that `bin/swain` is the canonical launcher ([ADR-033](../Active/(ADR-033)-Born-in-Worktree-Session-Isolation.md)) and supports all runtimes ([EPIC-056](../../epic/Complete/(EPIC-056)-Worktree-Isolation-Redesign/(EPIC-056)-Worktree-Isolation-Redesign.md)), the `.claude/` coupling serves no purpose.

The dual path causes concrete problems:

- **gitignore** lists both `.worktrees/` and `.claude/worktrees/` — easy to miss one when updating.
- **Permission settings** in `.claude/settings.local.json` accumulate stale entries referencing `.claude/worktrees/<branch>`.
- **Detection scripts** (`detect-worktree-links.sh`) and **tests** use `.claude/worktrees/` in fixtures, mixing "path we create" with "path we flag as bad."
- **Skill docs** (`swain-sync`) reference `.claude/worktrees/` in examples, confusing contributors about the canonical path.
- **Runtime coupling** — `.claude/` is a Claude Code convention. Gemini CLI, Codex, Copilot, and Crush have no reason to write there.

## Decision

`.worktrees/` is the single canonical worktree parent directory. There is no fallback. All code that creates, references, or validates worktree paths uses `.worktrees/` exclusively.

Specifically:

1. `choose_worktree_parent()` in `bin/swain` returns `$base_root/.worktrees` unconditionally — no directory existence check, no `git check-ignore` validation, no `.claude/worktrees` branch.
2. `.gitignore` drops the `.claude/worktrees/` entry.
3. Permission entries and skill docs update to `.worktrees/`.
4. Detection scripts **keep** `.claude/worktrees/` as a flagged pattern — post-migration, any such reference in a script is a bug, so the detection is now a safety net rather than a false positive.
5. Test fixtures that simulate worktree creation update to `.worktrees/`. Test fixtures that detect bad paths keep `.claude/worktrees/` (they test the safety net).

## Alternatives Considered

**Keep the fallback for backward compatibility.** Rejected — there are no consumer projects with `.claude/worktrees/` directories that lack `.worktrees/`. The fallback adds branching logic that never fires in practice but increases cognitive load.

**Remove `.claude/worktrees/` from detection scripts too.** Rejected — the detection pattern catches a real class of bugs (hardcoded paths from the old convention). Keeping it costs nothing and catches regressions.

## Consequences

**Positive:**
- `choose_worktree_parent()` drops from 14 lines to 3 — no branching, no validation, no fallback.
- One gitignore entry instead of two.
- Runtime-neutral — no `.claude/` assumption baked into the launcher.
- Detection scripts become strictly more useful: any `.claude/worktrees/` reference they find is now always wrong.

**Negative:**
- Any existing `.claude/worktrees/` directories need a one-time manual migration: `git worktree move` or remove-and-recreate. This is an operator step, not automated.
- Historical artifacts (completed specs, retros, tickets) still reference `.claude/worktrees/` — these are not rewritten, since they are historical records.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-05 | | Initial creation — user-requested |
