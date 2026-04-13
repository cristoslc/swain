---
title: "swain-bridge Daemon Mode"
artifact: SPEC-295
type: enhancement
status: Active
phase: Implementation
parent-initiative: INITIATIVE-006
linked-artifacts:
  - RUNBOOK-003
  - DESIGN-025
author: cristos
created: 2026-04-07
last-updated: 2026-04-07
depends-on-artifacts: []
source-issue: ""
---

## Summary

Add `--daemon` flag to `bin/swain-bridge` so the untethered operator bridge runs in the background, freeing the terminal for swain work while maintaining Zulip ↔ opencode connectivity.

## Problem

Current `swain-bridge` blocks the terminal (waits on child processes at line 84). User cannot use swain in the same terminal session while the bridge is running.

## Acceptance Criteria

- [ ] `--daemon` flag starts opencode serve + untethered-host in background, fully detached from terminal
- [ ] PIDs written to `/tmp/swain-bridge.pid` for later cleanup
- [ ] Logs redirected to `/tmp/swain-bridge.log`
- [ ] `--stop` flag reads PID file and gracefully stops both processes
- [ ] `--status` flag reports running/stopped with health info
- [ ] Default behavior (no flags) remains unchanged — foreground, blocking
- [ ] opencode serve health check still runs before starting bridge

## Scope

**In scope:**
- Modify `bin/swain-bridge` shell script
- Add daemon mode signal handling
- PID file management
- Log redirection
- Stop and status commands

**Out of scope:**
- Changes to `untethered-host` Python code
- opencode serve modifications
- Domain config changes

## Implementation Notes

1. Preserve existing cleanup trap for foreground mode
2. Daemon mode needs separate signal handling (no trap on EXIT)
3. Use `nohup` or double-fork pattern for full detachment
4. Health check endpoint: `http://127.0.0.1:$PORT/global/health`
5. PID file format: first line opencode PID, second line bridge PID

## Testing

- Manual: start daemon, verify terminal is free, send Zulip message, verify response
- Manual: `--stop` cleanly shuts down both processes
- Manual: `--status` shows correct state
- Regression: foreground mode still works as before

## Lifecycle

| Phase | Date | Commit |
|-------|------|--------|
| Proposed | 2026-04-07 | — |
| Active | 2026-04-07 | — |
| Implementation | 2026-04-07 | — |
| Complete | 2026-04-07 | — |

## Verification

**Test results:**
- `--daemon` starts both processes, writes PID file, exits immediately ✅
- `--status` shows running state with health check ✅
- `--stop` cleanly terminates both processes ✅
- Foreground mode preserved (blocking `wait`) ✅
- Terminal free for swain work while daemon runs ✅
