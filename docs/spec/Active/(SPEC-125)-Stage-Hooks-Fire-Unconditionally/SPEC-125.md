---
title: "swain-stage hooks fire unconditionally even when stage is not active"
artifact: SPEC-125
track: implementable
status: Implementation
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: bug
parent-epic: ""
parent-initiative: INITIATIVE-015
linked-artifacts:
  - SPEC-127
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# swain-stage hooks fire unconditionally even when stage is not active

## Problem Statement

The hooks in `.claude/settings.json` register `stage-status-hook.sh` on PostToolUse, Stop, SubagentStart, and SubagentStop with empty matchers. They fire on every event in every session regardless of whether swain-stage is active (tmux session with MOTD panel running). This causes unnecessary script execution and error noise in non-stage sessions.

## External Behavior

**Inputs:** Hook events from Claude Code (PostToolUse, Stop, SubagentStart, SubagentStop)
**Preconditions:** swain-stage is not active (no tmux session, no MOTD panel)
**Expected output:** Hook exits silently with code 0, no file writes
**Constraints:** Must not break stage functionality when stage IS active

## Acceptance Criteria

- **Given** a session where `$TMUX` is unset, **When** any hook event fires, **Then** `stage-status-hook.sh` exits 0 immediately without writing to `stage-status.json`
- **Given** a session inside tmux with the MOTD panel running, **When** any hook event fires, **Then** `stage-status-hook.sh` operates normally

## Reproduction Steps

1. Open a Claude Code session in a non-tmux terminal in the swain project
2. Perform any tool use (triggers PostToolUse hook)
3. Observe the hook runs and writes to `stage-status.json` unnecessarily
4. End the session (triggers Stop hook) — same unnecessary execution

## Severity

low

## Expected vs. Actual Behavior

**Expected:** Hook is a silent no-op when swain-stage is not active.

**Actual:** Hook runs on every event, writes status JSON, and may error if the environment is degraded.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Hook exits 0 immediately when `$TMUX` is unset | `skills/swain-stage/scripts/stage-status-hook.sh` lines 10-11: `[ -z "${TMUX:-}" ] && exit 0` — guard fires before any file writes or python execution | Pass |
| Guard uses safe variable expansion | Uses `${TMUX:-}` (default-empty) rather than bare `$TMUX`, so it is safe under `set -u` | Pass |
| Stage functionality unaffected when tmux is active | Guard only exits when `TMUX` is unset; all case branches below line 11 remain unchanged | Pass |

## Scope & Constraints

- Fix is limited to adding a guard clause at the top of `stage-status-hook.sh`
- Guard should check `$TMUX` environment variable as the primary signal
- Do not modify the hook registration in `settings.json` — the guard belongs in the script

## Implementation Approach

1. Add `[ -z "$TMUX" ] && exit 0` as the first executable line in `skills/swain-stage/scripts/stage-status-hook.sh`
2. Verify hook is silent in non-tmux sessions
3. Verify hook still works in tmux sessions

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation — user-reported bug |
| Implementation | 2026-03-20 | d8234a6 | Guard added at lines 10-11 of `stage-status-hook.sh`; all acceptance criteria verified |
