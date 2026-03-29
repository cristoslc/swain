---
title: "Orphaned Stage-Status Hooks Fire on Every Event"
artifact: SPEC-185
track: implementable
status: Complete
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-015
linked-artifacts:
  - SPEC-177
  - SPEC-125
  - SPEC-127
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Orphaned Stage-Status Hooks Fire on Every Event

## Problem Statement

[SPEC-177](../../Active/(SPEC-177)-Remove-Tmux-Swain-Stage/(SPEC-177)-Remove-Tmux-Swain-Stage.md) removed `skills/swain-stage/scripts/stage-status-hook.sh` (commit c894456) but did not remove the four hook registrations in `.claude/settings.json` that reference it. Every PostToolUse, Stop, SubagentStart, and SubagentStop event fires the deleted script, producing a non-blocking error on every hook invocation in every session.

## Desired Outcomes

Sessions run without spurious hook errors. The operator sees clean output instead of four "No such file or directory" errors per hook cycle.

## External Behavior

**Inputs:** Any Claude Code hook event (PostToolUse, Stop, SubagentStart, SubagentStop)

**Preconditions:** `.claude/settings.json` registers `stage-status-hook.sh` on all four events; the script no longer exists on disk.

**Outputs:** Each event produces:
```
Stop hook error: Failed with non-blocking status code: bash:
/Users/cristos/Documents/code/swain/skills/swain-stage/scripts/stage-status-hook.sh: No such file or directory
```

**Postconditions (after fix):** No hook errors from stage-status-hook references. `.claude/settings.json` either has an empty `hooks` object or no `hooks` key at all.

## Acceptance Criteria

- **AC-1:** Given `.claude/settings.json` has been updated, when any hook event fires (PostToolUse, Stop, SubagentStart, SubagentStop), then no "stage-status-hook" error appears in the session output.
- **AC-2:** Given the fix is applied, when `.claude/settings.json` is read, then it contains no references to `stage-status-hook.sh`.
- **AC-3:** Given other projects may define their own hooks, when the fix is applied, then the `hooks` key structure remains valid JSON (empty object `{}` is acceptable).

## Reproduction Steps

1. Start any Claude Code session in the swain project directory.
2. Perform any action that triggers a hook event (e.g., use a tool, end a conversation, start/stop a subagent).
3. Observe the error in the session output stream.

## Severity

high — affects every session, every hook event. Purely cosmetic (non-blocking errors) but constant noise.

## Expected vs. Actual Behavior

**Expected:** Hook events fire with no errors (no hooks registered, or hooks point to valid scripts).

**Actual:** Every hook event produces a "No such file or directory" error for `stage-status-hook.sh`.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1: No stage-status-hook errors on hook events | Removed all four hook entries from .claude/settings.json | Pass |
| AC-2: No references to stage-status-hook.sh in settings | Inspected settings.json — contains `{}` only | Pass |
| AC-3: Valid JSON structure preserved | settings.json is valid empty JSON object | Pass |

## Scope & Constraints

- Fix is limited to removing the four orphaned hook entries from `.claude/settings.json`.
- Do not add new hooks or modify any other settings.
- The fix completes the cleanup that SPEC-177 should have included.

## Implementation Approach

1. Edit `.claude/settings.json` to remove all four hook registrations (PostToolUse, Stop, SubagentStart, SubagentStop) that reference `stage-status-hook.sh`.
2. Leave a valid JSON structure (empty `hooks` object or remove the key).
3. Verify by starting a session and confirming no hook errors appear.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation |
| Complete | 2026-03-28 | -- | Removed orphaned hooks from .claude/settings.json |
