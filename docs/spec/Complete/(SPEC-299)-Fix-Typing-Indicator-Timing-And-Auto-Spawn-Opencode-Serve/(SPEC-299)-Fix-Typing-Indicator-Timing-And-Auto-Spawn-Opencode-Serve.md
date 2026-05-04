---
id: SPEC-299
title: "Fix Typing Indicator Timing And Auto-Spawn Opencode Serve"
type: bug
priority-weight: high
status: Complete
created: 2026-04-07
last-updated: 2026-04-07
swain-do: required
---

# SPEC-299: Fix Typing Indicator Timing And Auto-Spawn Opencode Serve

## Background

The untethered bridge had two UX issues in the Zulip → opencode serve pipeline:

1. **Typing indicator delay**: The typing indicator didn't start until `session_spawned` event fired, which happens after the server health check completes. This meant no visual feedback during the several seconds of server startup time.

2. **Server startup race condition**: If `opencode serve` wasn't already running on port 4097, the bridge would error with "opencode serve not reachable" instead of automatically spawning it.

## Reproduction Steps

### Issue 1: Typing Indicator Delay
1. Start untethered bridge: `uv run untethered-host --domain personal`
2. Send a message in Zulip to trigger a session
3. Observe: No typing indicator appears until after the server health check completes

### Issue 2: Server Not Running
1. Kill any existing `opencode serve` process
2. Start untethered bridge
3. Send a message to trigger a session
4. Observe: Error message "opencode serve not reachable" instead of auto-spawning

## Severity

High — impacts operator experience and creates friction when the server isn't pre-started.

## Expected Behavior

- Typing indicator should start **immediately** when session creation begins
- Server should auto-spawn if not already running, with appropriate timeouts

## Actual Behavior

- Typing indicator started only after successful health check
- Server startup was manual — bridge would fail if server not pre-running

## Acceptance Criteria

- [x] **Given** the operator sends a message to trigger a session, **When** session creation begins, **Then** the typing indicator starts immediately (before any blocking operations)

- [x] **Given** `opencode serve` is not running on the expected port, **When** the bridge attempts to create a session, **Then** it automatically spawns the server with a 60s health check timeout

- [x] **Given** the server fails to spawn, **When** the health check times out, **Then** a clear error message is shown to the operator

- [x] **Given** the server spawns successfully, **When** the session completes, **Then** the typing indicator stops via the existing TextBatcher on_flush callback

## Implementation Summary

### Changes Made

1. **protocol.py**: Added `Event.session_starting()` — a new event type emitted before blocking operations begin

2. **project.py** (`_cmd_start_session_with_worktree`):
   - Emit `session_starting` event immediately after creating the adapter
   - If health check fails, attempt to auto-spawn the server
   - Retry health check after spawn with extended 60s timeout

3. **zulip_chat.py** (`_relay_events`):
   - Start typing indicator on `session_starting` event (moved from `session_spawned`)
   - `session_spawned` now passes silently (typing already active)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Typing starts immediately | Code review: zulip_chat.py line 344 now starts on `session_starting` | Pass |
| Auto-spawn works | Manual test: killed opencode serve, triggered session — server spawned automatically | Pass |
| Error handling | Code review: proper error paths if spawn fails | Pass |
| Lifecycle coupling | RETRO-2026-04-07-untethered-operator-final.md confirms indicator stops on batch flush | Pass |

## Linked Artifacts

- **Addresses**: VISION-006 (Untethered Operator)
- **Related**: SPEC-296 (Worktree Session Isolation), SPEC-292 (OpenCode Server Adapter)

## Lifecycle

| Phase | Date | Commit |
|-------|------|--------|
| Active → Complete | 2026-04-07 | 79927f21 |

---
