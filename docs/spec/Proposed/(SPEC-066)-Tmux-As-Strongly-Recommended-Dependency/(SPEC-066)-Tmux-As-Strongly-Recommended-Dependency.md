---
title: "Tmux as Strongly Recommended Dependency"
artifact: SPEC-066
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Tmux as Strongly Recommended Dependency

## Problem Statement

`swain-stage` hard-requires tmux and silently no-ops when it is absent. `swain-session` degrades when not running inside a tmux session, with no diagnostic surfaced to the user. Users who install swain without tmux receive no guidance that a significant portion of swain's session model is unavailable. Unlike superpowers (which is fully optional with no capability loss), tmux enables session staging, pane-aware naming, and session context features that are core to the swain workflow. Tmux should be surfaced as a strongly recommended dependency — checked by `swain-doctor`, documented in onboarding material, with graceful degradation when absent rather than silent failure.

## External Behavior

Changes across affected skills:

| Skill | Current behavior | New behavior |
|-------|-----------------|--------------|
| `swain-doctor` | No tmux check | Checks `which tmux`; if not found, emits `warn` diagnostic: `"tmux not found — swain-stage and session features unavailable. Install: brew install tmux"`; if found but `$TMUX` is unset, no diagnostic (presence check only, not session check) |
| `swain-stage` | Fails silently or errors unexpectedly when tmux is absent | Returns early with `"tmux not found — install with \`brew install tmux\`"` when tmux binary is missing; returns early with `"tmux not active — swain-stage requires a tmux session. Start tmux first."` when tmux is installed but not in a session |
| `swain-session` | Uses tmux for tab naming/pane context; silently skips when not in tmux | Notes in startup output when not running inside a tmux session: `"[note] Not in a tmux session — session tab and pane features unavailable"` |
| Onboarding docs | tmux not mentioned alongside superpowers | `swain-init`, `AGENTS.md`, or equivalent onboarding material lists tmux alongside superpowers as a recommended tool with install hint |

**swain-doctor tmux check specifics:**

- Uses `which tmux` (not `tmux -V`) — binary presence only, no version check, completes in under 1 second
- Distinguishes two states: (a) tmux binary not found → `warn` diagnostic with install hint; (b) tmux installed but operator is not in a tmux session → no diagnostic from doctor (session state is not doctor's concern)
- Diagnostic severity: `warn` (not `error`, not `info`) — tmux absence does not block other swain functionality

## Acceptance Criteria

- Given tmux is not installed, when `swain-doctor` runs, then a `warn` diagnostic is emitted naming the missing tool and the install command: `"tmux not found — swain-stage and session features unavailable. Install: brew install tmux"`
- Given tmux is installed and `swain-doctor` runs, then no tmux diagnostic appears (regardless of whether operator is inside a tmux session)
- Given tmux is installed but the operator is not in a tmux session, when `swain-stage` runs, then it exits with: `"tmux not active — swain-stage requires a tmux session. Start tmux first."`
- Given tmux is not installed, when `swain-stage` runs, then it exits with: `"tmux not found — install with \`brew install tmux\`"`
- Given tmux is installed and active, when `swain-stage` runs, then it proceeds normally with no tmux-related message
- Given the operator is not in a tmux session, when `swain-session` runs, then startup output includes the note: `"[note] Not in a tmux session — session tab and pane features unavailable"`
- `swain-doctor` tmux check completes in under 1 second (`which` command only, no network calls)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Do not make tmux a hard requirement — all tmux-gated features degrade gracefully; no other swain functionality is blocked when tmux is absent
- Do not auto-install tmux
- Do not check tmux version — binary presence (`which tmux`) is sufficient
- Diagnostic severity must be `warn`, not `error` or `info`
- The onboarding update must be additive — do not restructure existing onboarding content, only add tmux alongside the existing superpowers recommendation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | -- | Formalizes tmux as strongly recommended dependency alongside superpowers |
