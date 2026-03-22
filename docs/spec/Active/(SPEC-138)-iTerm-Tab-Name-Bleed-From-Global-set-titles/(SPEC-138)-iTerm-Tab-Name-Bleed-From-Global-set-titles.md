---
title: "iTerm Tab Name Bleed From Global set-titles"
artifact: SPEC-138
track: implementable
status: Active
author: operator
created: 2026-03-21
last-updated: 2026-03-21
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-056
  - DESIGN-001
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# iTerm Tab Name Bleed From Global set-titles

## Problem Statement

When multiple iTerm tabs each host a tmux session managed by swain, inactive tabs display the **active** tab's swain window name instead of their own. The tmux window name is correct upon switching to the tab, but the iTerm tab title is wrong while the tab is in the background. This is confusing for the operator who relies on tab names to identify sessions at a glance.

## External Behavior

**Precondition:** Two or more iTerm tabs, each running a tmux session with swain-managed tab names (via `swain-tab-name.sh --auto`).

**Current behavior:** All iTerm tabs show the title of whichever swain session is currently focused. Switching focus to Tab A sets all other tabs' iTerm titles to Tab A's window name.

**Fixed behavior:** Each iTerm tab retains its own session's window name regardless of which tab is focused. Tab switching does not affect other tabs' displayed titles.

## Acceptance Criteria

1. **Given** two iTerm tabs each running a swain tmux session with different projects, **when** Tab A is focused, **then** Tab B's iTerm tab title still shows Tab B's project name.
2. **Given** the fix is applied, **when** `swain-tab-name.sh --auto` runs in any session, **then** no global tmux `set-titles` or `set-titles-string` options are set.
3. **Given** a pane-focus-in hook fires, **when** the hook updates the title, **then** only the client terminal attached to that session receives the OSC title escape.
4. **Given** `swain-tab-name.sh --reset` is run, **when** the reset completes, **then** global `set-titles` is turned off (cleanup of prior state) and the specific client's terminal title is reset.

## Reproduction Steps

1. Open iTerm. Create two tabs.
2. In each tab, start a tmux session in a different git project.
3. Run `swain-tab-name.sh --auto` in each session (or let swain-session auto-invoke it).
4. Focus Tab A. Observe Tab B's iTerm tab title — it now shows Tab A's project name.
5. Focus Tab B. Observe Tab A's iTerm tab title — it now shows Tab B's project name.

## Severity

medium

## Expected vs. Actual Behavior

**Expected:** Each iTerm tab displays the title of its own tmux session's swain window, independent of focus state.

**Actual:** All iTerm tabs display the title of the currently focused tab's swain window, because `tmux set-option -g set-titles-string "#W"` is a server-global option that broadcasts the focused client's window name to all client terminals.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- Fix must be backward-compatible with existing swain sessions (degrade gracefully if `list-clients` fails).
- The tmux `rename-window` mechanism (for within-tmux window tabs) is NOT affected — only the outer iTerm tab title propagation.
- Fix applies to iTerm + tmux on macOS. Other terminal emulators are out of scope but should not regress.

## Implementation Approach

### Root cause

`swain-tab-name.sh` line 53–54 sets `set-titles on` and `set-titles-string "#W"` as **global** (`-g`) tmux options. This tells the tmux server to propagate the active window name of the focused client to ALL client terminals. Since each iTerm tab is a separate tmux client, they all receive the focused client's title.

### Fix

1. Remove the global `set-option -g set-titles on` and `set-option -g set-titles-string "#W"` from `set_title()`.
2. Replace with direct OSC escape writes to the specific client's tty:
   - Use `tmux list-clients -t <session> -F '#{client_tty}'` to find the terminal device for the current session's client.
   - Write `\033]1;TITLE\007` (iTerm tab) and `\033]0;TITLE\007` (generic title) directly to that tty.
3. In `reset_title()`, turn off global `set-titles` to clean up previously-set state, and write the reset escape to the specific client tty.
4. Add a cleanup call: `set-option -g set-titles off` in both `set_title` and `reset_title` to undo prior global state from older script runs.

### TDD cycle

- **AC 1–3:** Update `test-tab-name.sh` with a multi-session test that verifies per-client title isolation.
- **AC 4:** Extend the reset test to verify global `set-titles` is off after reset.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Initial creation |
