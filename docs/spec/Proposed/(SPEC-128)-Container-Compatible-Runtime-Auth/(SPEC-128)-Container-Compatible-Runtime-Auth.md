---
title: "Container-Compatible Runtime Auth Commands"
artifact: SPEC-128
track: implementable
status: Proposed
type: enhancement
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-initiative: INITIATIVE-013
parent-vision: VISION-002
depends-on-artifacts:
  - SPIKE-035
linked-artifacts:
  - DESIGN-005
  - SPEC-092
  - SPEC-126
  - SPIKE-035
acceptance-criteria:
  - Every runtime in swain-box _login_cmd has a container-compatible auth command verified by SPIKE-035
  - _login_cmd table updated with device-auth or alternative commands where needed
  - _known_issue_microvm table updated to reflect auth limitations per runtime
  - Auth step in swain-box displays the correct login command for the selected isolation mode
swain-do: required
---

# Container-Compatible Runtime Auth Commands

## Context

swain-box's `_login_cmd` function maintains a table of login commands per runtime. Some of these commands use browser-based OAuth that cannot complete inside containers (the browser callback to localhost is unreachable from inside a VM or container). Each runtime needs its container-compatible auth command verified and the table updated.

The codex runtime was the first known case: `codex login` opens a browser that can't call back, but `codex login --device-auth` uses a device code flow that works. This pattern may apply to other runtimes.

## Scope

**In scope:**
- Update `_login_cmd` in `swain-box` with container-compatible commands for all runtimes, based on SPIKE-035 findings
- Update `_known_issue_microvm` table if any runtimes have microVM-specific auth issues
- Make `_login_cmd` isolation-aware if different commands are needed for microVM vs container modes
- Document which runtimes support subscription auth in containers vs requiring API keys

**Out of scope:**
- Adding new runtimes to swain-box
- Changes to the auth type selection menu (step 2)
- Credential persistence or rotation

## Acceptance Criteria

- Every runtime in swain-box `_login_cmd` has a container-compatible auth command verified by SPIKE-035
- `_login_cmd` table updated with device-auth or alternative commands where needed
- `_known_issue_microvm` table updated to reflect auth limitations per runtime
- Auth step in swain-box displays the correct login command for the selected isolation mode

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-19 | | Initial creation, blocked on SPIKE-035 |
