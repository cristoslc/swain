---
title: "Tmux as Strongly Recommended Dependency"
artifact: SPEC-066
track: implementable
status: Complete
author: cristos
created: 2026-03-17
last-updated: 2026-03-18
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
| `swain-doctor` | No tmux check | Checks `which tmux`; if not found, offers to run `brew install tmux`; if found but `$TMUX` is unset, no diagnostic (presence check only, not session check) |
| `swain-stage` | Fails silently or errors unexpectedly when tmux is absent | When tmux binary is missing: reports `"tmux not found"` and the skill offers to install it via `brew install tmux`, re-running the subcommand on acceptance; when tmux is installed but not in a session: exits with `"tmux not active — swain-stage requires a tmux session. Start tmux first."` |
| `swain-session` | Uses tmux for tab naming/pane context; silently skips when not in tmux | Checks `which tmux` on startup; if not installed, offers to install; if installed but not in a session, shows note: `"[note] Not in a tmux session — session tab and pane features unavailable"` |
| Onboarding docs | tmux not mentioned alongside superpowers | `swain-init` Phase 4.4 checks for tmux; if missing, offers to install interactively (same pattern as superpowers offer) |

**swain-doctor tmux check specifics:**

- Uses `which tmux` (not `tmux -V`) — binary presence only, no version check, completes in under 1 second
- Distinguishes two states: (a) tmux binary not found → `warn` diagnostic with install hint; (b) tmux installed but operator is not in a tmux session → no diagnostic from doctor (session state is not doctor's concern)
- Diagnostic severity: `warn` (not `error`, not `info`) — tmux absence does not block other swain functionality

## Acceptance Criteria

- Given tmux is not installed, when `swain-doctor` runs, then the skill offers to run `brew install tmux` for the user
- Given the user accepts the install offer from `swain-doctor`, then `brew install tmux` is run on their behalf
- Given tmux is installed and `swain-doctor` runs, then no tmux diagnostic appears (regardless of whether operator is inside a tmux session)
- Given tmux is installed but the operator is not in a tmux session, when `swain-stage` runs, then it exits with: `"tmux not active — swain-stage requires a tmux session. Start tmux first."`
- Given tmux is not installed, when `swain-stage` runs, then the skill offers to install tmux and re-run the subcommand on acceptance
- Given tmux is installed and active, when `swain-stage` runs, then it proceeds normally with no tmux-related message
- Given tmux is not installed, when `swain-session` runs, then the skill offers to install tmux
- Given tmux is installed but `$TMUX` is not set, when `swain-session` runs, then startup output includes the note: `"[note] Not in a tmux session — session tab and pane features unavailable"` (no install offer)
- Given tmux is not installed, when `swain-init` runs, then Phase 4.4 offers to install tmux interactively and runs `brew install tmux` on acceptance
- `swain-doctor` tmux check completes in under 1 second (`which` command only, no network calls)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| swain-doctor offers to install when tmux missing | `tool-availability.md`: tmux row has `offer to install` degradation note; new `## Install offers` section instructs agent to prompt and run install on acceptance | Pass |
| swain-doctor install offer runs brew on acceptance | `tool-availability.md` Install offers section: "Run the command if the user accepts" with `<install-hint>` = `brew install tmux` | Pass |
| swain-doctor: no diagnostic when tmux installed | `tool-availability.md` reporting format: "Only flag items that need attention" — tmux `ok` line is silent | Pass |
| swain-stage: exits with not-active message when installed but no session | `env TMUX="" bash swain-stage.sh layout review` → `"tmux not active — swain-stage requires a tmux session. Start tmux first."` EXIT:1 | Pass |
| swain-stage: offers to install when binary missing | `swain-stage/SKILL.md` error handling: "If the script reports tmux not found, offer to install it" with `brew install tmux` and re-run on acceptance | Pass |
| swain-stage: proceeds normally when tmux active | `require_tmux()` only exits on two error paths; no regression to normal flow | Pass |
| swain-session: offers to install when tmux not installed | `swain-session/SKILL.md` Step 1: `which tmux` check → if not found, offer `brew install tmux` | Pass |
| swain-session: shows note (no offer) when installed but not in session | `swain-session/SKILL.md` Step 1: if `which tmux` succeeds but `$TMUX` unset → `[note] Not in a tmux session — session tab and pane features unavailable` | Pass |
| swain-init Phase 4.4 offers interactive install | `swain-init/SKILL.md` Phase 4.4: asks yes/no, runs `brew install tmux` on acceptance, warns on failure | Pass |
| swain-doctor tmux check under 1 second | `tool-availability.md`: check is `which tmux` — binary lookup only, no network calls | Pass |

## Scope & Constraints

- Do not make tmux a hard requirement — all tmux-gated features degrade gracefully; no other swain functionality is blocked when tmux is absent
- Do not auto-install tmux
- Do not check tmux version — binary presence (`which tmux`) is sufficient
- Diagnostic severity must be `warn`, not `error` or `info`
- The onboarding update must be additive — do not restructure existing onboarding content, only add tmux alongside the existing superpowers recommendation

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | 4090f28 | Formalizes tmux as strongly recommended dependency alongside superpowers |
| NeedsManualTest | 2026-03-18 | 4610918 | All tasks verified; offer-to-install behavior implemented across swain-doctor, swain-stage, swain-session, swain-init |
| Complete | 2026-03-18 | 30b5a1a | All acceptance criteria verified; spec-verify.sh exit 0 |
