---
title: "bin/swain Missing Tmux Wrapping"
artifact: SPEC-286
track: implementable
status: Active
author: cristos
created: 2026-04-05
last-updated: 2026-04-05
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - EPIC-056
  - DESIGN-004
  - SPEC-245
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# SPEC-286: bin/swain Missing Tmux Wrapping

## Problem Statement

The shell launcher function `swain()` in launcher templates delegates to `bin/swain` via `exec` when it exists. But `bin/swain` has no tmux awareness — it launches the runtime as a bare child process. The tmux wrapping logic (create session outside tmux, rename window inside tmux) only exists in the shell function's fallback path, which is never reached when `bin/swain` is present.

## Desired Outcomes

Operators get a tmux-wrapped session when launching swain from outside tmux, matching the behavior they had before `bin/swain` took over. Inside tmux, the window is renamed to reflect the session purpose. This restores the expected UX described in [DESIGN-004](../../../design/Active/(DESIGN-004)-swain-stage-Interaction-Design/(DESIGN-004)-swain-stage-Interaction-Design.md)'s flow diagram.

## External Behavior

**Outside tmux (`$TMUX` unset):**
- `bin/swain` wraps the runtime launch in `tmux new-session`
- Session name derives from the worktree context slug (e.g., `swain-bugfix-tmux`)
- Operator lands inside the tmux session with the runtime running

**Inside tmux (`$TMUX` set):**
- `bin/swain` renames the current tmux window to reflect the session purpose
- Runtime launches directly in the current pane (no nesting)

**`--trunk` mode:**
- Same tmux behavior applies (wrap or rename)

**Dry-run mode (`--_dry_run`):**
- Reports tmux intent (`tmux: new-session` or `tmux: rename-window`) but does not act

## Acceptance Criteria

- **AC1**: Given `$TMUX` is unset, when `bin/swain` launches a runtime, then the runtime runs inside a new tmux session named after the worktree context slug
- **AC2**: Given `$TMUX` is set, when `bin/swain` launches a runtime, then the current tmux window is renamed to reflect the session context
- **AC3**: Given `--_dry_run`, when `bin/swain` runs, then the output includes `tmux_action: new-session` or `tmux_action: rename-window` as appropriate
- **AC4**: Given tmux is not installed (`command -v tmux` fails), when `bin/swain` launches, then it falls back to direct launch with a warning: `warning: tmux not found; launching without session wrapping`

## Reproduction Steps

1. Ensure `bin/swain` exists and is executable
2. Open a terminal that is NOT inside tmux
3. Run `./bin/swain "test session"`
4. Observe: runtime launches in the bare terminal — no tmux session is created
5. Expected: runtime launches inside a new tmux session

## Severity

high — the primary launch path bypasses tmux, breaking session persistence and the tab/window naming UX that operators rely on

## Expected vs. Actual Behavior

**Expected:** `bin/swain` creates a tmux session when outside tmux, renames the window when inside tmux, per [DESIGN-004](../../../design/Active/(DESIGN-004)-swain-stage-Interaction-Design/(DESIGN-004)-swain-stage-Interaction-Design.md) flow.

**Actual:** `bin/swain` runs `eval "$cmd" &` directly — no tmux interaction at all.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only touches `phase3_launch_runtime` in `skills/swain/scripts/swain`
- Does not change the launcher templates — they already delegate to `bin/swain`
- Signal forwarding and post-runtime cleanup must still work inside the tmux session
- The child-process model (not `exec`) from [SPEC-245](../../Complete/(SPEC-245)-bin-swain-Redesign/(SPEC-245)-bin-swain-Redesign.md) AC4 is preserved
- tmux session name must be safe (no special characters that tmux rejects)

## Implementation Approach

1. Add a `tmux_session_name` helper that sanitizes the worktree context slug for tmux (alphanumeric, hyphens, underscores only, truncated to 32 chars)
2. In `phase3_launch_runtime`, after building `cmd` and before launching:
   - If `$TMUX` is unset and `command -v tmux` succeeds: wrap the launch in `tmux new-session -s "$session_name" "$cmd"`
   - If `$TMUX` is set: call `tmux rename-window "$session_name"` before launching the runtime
   - If tmux is not installed: warn and launch directly
3. Dry-run output gains a `tmux_action` field
4. BDD tests cover all four ACs using `--_dry_run` and `--_non_interactive` flags

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-05 | -- | Bug filed — tmux wrapping lost when bin/swain replaced shell function |
