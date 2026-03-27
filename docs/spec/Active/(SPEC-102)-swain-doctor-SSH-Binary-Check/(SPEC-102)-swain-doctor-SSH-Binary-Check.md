---
title: "swain-doctor SSH Binary Check"
artifact: SPEC-102
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-013
linked-artifacts:
  - EPIC-040
  - SPEC-092
  - SPEC-103
  - SPEC-104
  - SPEC-105
  - SPEC-106
  - SPEC-108
  - SPEC-112
  - SPEC-133
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# swain-doctor SSH Binary Check

## Problem Statement

swain-box sandboxes use SSH for connecting to Docker Sandboxes (microVMs). If `ssh` is not on the host PATH, sandbox creation succeeds but the connection step fails with an unhelpful error. swain-doctor should detect the missing binary at session start so the operator gets a clear advisory before attempting sandbox operations.

## External Behavior

**Precondition:** swain-doctor runs its tool-availability checks during session startup.

**New check:** swain-doctor verifies `ssh` is available on PATH via `command -v ssh`.

- **Present:** report `SSH binary ... ok` in the summary table. No further action.
- **Missing:** report `SSH binary ... warning` with advisory text: `ssh not found — required for Docker Sandbox (microVM) connections. Install via: brew install openssh (macOS) or apt install openssh-client (Linux).`

This is an **advisory** (non-blocking) check. Missing SSH does not prevent swain-doctor from completing — it warns the operator so they can install before attempting microVM sandbox operations.

**Preflight:** The lightweight preflight script (`swain-preflight.sh`) does NOT check for SSH. This is a doctor-only check because SSH is only needed for sandbox operations, not for general swain functionality.

## Acceptance Criteria

- Given swain-doctor runs and `ssh` is on PATH, when the summary table is printed, then a row shows `SSH binary ... ok`.
- Given swain-doctor runs and `ssh` is NOT on PATH, when the summary table is printed, then a row shows `SSH binary ... warning` with install hints for macOS and Linux.
- Given `ssh` is missing, when swain-doctor completes, then exit code is still 0 (advisory, not blocking).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Advisory only — does not block session startup or any other swain operation.
- Follows existing tool-availability check pattern (`command -v`).
- One new row in the doctor summary table; no new scripts or reference files needed.
- Does not check SSH key configuration (that's swain-keys' responsibility).

## Implementation Approach

1. Add `command -v ssh` check to swain-doctor's tool-availability checks in `references/tool-availability.md`.
2. Add the SSH binary row to the summary table format in SKILL.md.
3. Test: mock PATH without ssh, verify warning appears; restore PATH, verify ok appears.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | — | Initial creation |
