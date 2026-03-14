---
title: "MOTD Uncommitted File Display and Interactive Commit Button"
artifact: SPEC-042
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-011
linked-artifacts:
  - EPIC-011
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#13"
swain-do: required
---

# MOTD Uncommitted File Display and Interactive Commit Button

## Problem Statement

The MOTD header shows a generic "N changed" dirty-state string but does not distinguish staged from unstaged files. Additionally, there is no way to trigger a commit/push from within the MOTD panel — the user must switch context to a shell. GitHub #13 requested both staged/unstaged counts and a clickable commit button.

## External Behavior

### Uncommitted file display

The MOTD Textual TUI shows two distinct counts prominently:
- **Staged:** N files (green or highlighted when > 0)
- **Unstaged:** N files (yellow or muted when > 0)

These counts refresh on the same cadence as the rest of the status cache (every ~120s or on `--refresh`).

### Interactive commit button

A clickable button (or keybind) in the Textual TUI labeled **"Commit & Push"** (or similar):
1. On click/keypress, opens a new tmux pane (via `tmux split-window`) running `swain-push` (or `swain-sync`)
2. The pane auto-closes on success; stays open on failure so the user can see the error
3. The button is disabled (grayed out) when there are zero staged files

## Acceptance Criteria

- **Given** the repo has staged files, **When** the MOTD renders, **Then** the staged count is shown and non-zero, distinct from the unstaged count.
- **Given** the repo has unstaged but no staged files, **When** the MOTD renders, **Then** staged = 0 and unstaged > 0 are shown separately.
- **Given** the MOTD is running in a tmux session and there are staged files, **When** the user clicks the "Commit & Push" button, **Then** a new tmux pane opens running `swain-push`.
- **Given** `swain-push` succeeds in the pane, **When** it exits 0, **Then** the tmux pane closes automatically.
- **Given** `swain-push` fails in the pane, **When** it exits non-zero, **Then** the pane stays open with the error visible.
- **Given** there are zero staged files, **When** the MOTD renders, **Then** the "Commit & Push" button is visually disabled and non-interactive.
- **Given** the MOTD is running outside a tmux session, **When** the user attempts to click the button, **Then** a notice is shown ("Commit button requires tmux") — no crash.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- Textual TUI only — bash MOTD fallback is out of scope.
- Commit trigger mechanism: tmux pane spawn (confirmed most practical per #13 feasibility notes).
- Does not implement a signal-file or polling mechanism (out of scope per #13).
- Staged/unstaged counts sourced from `git diff --cached --name-only | wc -l` and `git diff --name-only | wc -l`.

## Implementation Approach

1. Add a `git_counts()` helper to the status cache refresh that returns `{staged: N, unstaged: N}`.
2. Update the Textual TUI header widget to show staged/unstaged counts as separate labeled fields.
3. Add a `Button` widget ("Commit & Push") to the TUI layout, enabled only when staged > 0.
4. Wire the button's `on_click` handler to `subprocess.run(["tmux", "split-window", "-h", "swain-push"])`.
5. Add a guard: if `TMUX` env var is unset, show an inline notice instead of spawning.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | ca755446db4a68c7429812fa6b8f2837856e7050 | Initial creation from EPIC-011 decomposition; linked to GitHub #13 |
