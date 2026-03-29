---
title: "Session End Operation"
artifact: SPEC-184
track: implementable
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: ""
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-019
linked-artifacts:
  - SPEC-183
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Session End Operation

## Problem Statement

When the operator finishes a session, there is no structured cleanup. Worktrees accumulate, deferred actions from sleep mode get lost, learnings evaporate, and the next session starts without context. The operator must manually check for uncommitted work, decide on worktree fate, and remember to bookmark.

## Desired Outcomes

The operator says "end" and gets a clean shutdown: uncommitted work is flagged, open tasks are surfaced, deferred actions are visible, the worktree is automatically kept or cleaned based on merge status, a session retro captures learnings, and a final bookmark provides continuity for the next session. The operator can then `/exit` knowing nothing was left behind.

## External Behavior

**Input:** Operator says "end", "wrap up", "done for today", "clean up session", "shut it down."

**Sequence:**

1. **Dirty check** — run `git status`. If uncommitted changes, warn loudly. Don't block.
2. **Open work check** — run `tk ready` and `tk status`. Surface open/in-progress tasks.
3. **Deferred actions check** — if sleep mode accumulated deferred actions, surface the list.
4. **Worktree decision** — `git merge-base --is-ancestor HEAD trunk`:
   - Merged (exit 0): clean up via `ExitWorktree` with discard.
   - Not merged (exit 1): keep worktree, bookmark for next session.
5. **Session retro** — invoke swain-retro with session scope. Attaches to EPIC if working under one; standalone otherwise.
6. **Final bookmark** — summary of what was accomplished, pending work, deferred actions.
7. **Inform operator:** "Session cleaned up. Safe to `/exit` or close the terminal."

**`SessionEnd` hook (safety net):** If the operator quits without running end, the hook writes a bookmark-only safety note ("session ended without cleanup"). It does not run the full sequence (retro, worktree decision require agent judgment).

**Script: `swain-session-end.sh`** performs deterministic checks and outputs JSON:
```json
{
  "dirty": false,
  "merged": true,
  "deferredActionCount": 0,
  "openTasks": 3
}
```

## Acceptance Criteria

- **AC-1:** Given uncommitted changes exist, when end runs, then the operator sees a warning with the dirty file list.
- **AC-2:** Given open tk tasks exist, when end runs, then the task list is surfaced with status.
- **AC-3:** Given sleep mode deferred actions exist in session.json, when end runs, then the deferred action list is surfaced.
- **AC-4:** Given the worktree branch is merged to trunk, when end runs, then `ExitWorktree` is called to clean up.
- **AC-5:** Given the worktree branch is NOT merged to trunk, when end runs, then the worktree is preserved and bookmarked.
- **AC-6:** Given end runs, then swain-retro is invoked with session scope before the final bookmark.
- **AC-7:** Given the operator quits without running end, then the `SessionEnd` hook writes a bookmark-only safety note.
- **AC-8:** `swain-session-end.sh` outputs valid JSON with dirty, merged, deferredActionCount, and openTasks fields.

## Scope & Constraints

- End does not auto-commit. Uncommitted changes at end time are anomalous (swain commits regularly) — warn, don't fix.
- End does not programmatically exit the runtime (no CLI supports this). It prepares the session for clean exit.
- The `SessionEnd` hook is Claude Code-specific. Other runtimes have no safety net.
- Hook commands must use `find`-based script discovery to work from worktrees.
- swain-init installs the `SessionEnd` hook during onboarding.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation from brainstorming design |
