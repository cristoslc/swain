---
title: "Doctor .agents/bin/ Auto-Repair"
artifact: SPEC-186
track: implementation
status: Complete
author: cristos
created: 2026-03-28
last-updated: 2026-03-29
parent-epic: EPIC-047
priority-weight: high
depends-on-artifacts: []
linked-artifacts:
  - ADR-019
  - EPIC-029
  - SPEC-137
---

# Doctor .agents/bin/ Auto-Repair

## Goal

swain-doctor detects missing or broken `.agents/bin/` symlinks for agent-facing scripts and auto-repairs them. This is the runtime safety net that ensures consumer projects have working symlinks even if swain-init wasn't run or a skill update added new scripts.

## Behavior

### Discovery

Scan the skill tree for agent-facing scripts. An agent-facing script is any executable file under `skills/*/scripts/` that is **not** listed in the operator-facing registry (initially: `swain`, `swain-box`).

### Health check per script

For each discovered script, check `.agents/bin/<script-name>`:

| Status | Condition | Action |
|--------|-----------|--------|
| **ok** | Symlink exists and resolves to the correct skill-tree target | Silent |
| **missing** | No file at `.agents/bin/<script-name>` | Create symlink, report "repaired" |
| **stale** | Symlink exists but points to wrong target | Update symlink, report "repaired (stale)" |
| **conflict** | A real file (not a symlink) exists | Warn with manual remediation instructions |

### Symlink creation

```bash
mkdir -p .agents/bin
# Compute relative path from .agents/bin/ to skill-tree script
ln -sf "../../skills/<skill>/scripts/<script-name>" ".agents/bin/<script-name>"
```

Symlinks use **relative paths** so they work regardless of clone location.

### Integration point

Add this check to `swain-preflight.sh`, after the existing trunk detection block. When the preflight finds `.agents/bin/swain-trunk.sh` missing, it should auto-create the symlink instead of just reporting an issue — then proceed with trunk detection as normal.

For the full doctor (SKILL.md), add a new "Agent script symlinks (.agents/bin/)" section using the standard detection/response/status format.

## Deliverables

- Updated `swain-preflight.sh` — auto-repair `.agents/bin/` symlinks before trunk detection
- Updated `swain-doctor/SKILL.md` — new health check section for `.agents/bin/`

## Test Plan

- T1: Run preflight on a repo with no `.agents/bin/` — directory and symlinks are created, no error reported
- T2: Run preflight on a repo with correct `.agents/bin/swain-trunk.sh` — silent pass
- T3: Run preflight on a repo with stale symlink (points to wrong path) — symlink updated
- T4: Run preflight on a repo with a real file at `.agents/bin/swain-trunk.sh` — warning, no overwrite

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Created as EPIC-047 child; minimum viable fix for consumer project symlinks |
| Complete | 2026-03-29 | — | All 4 ACs verified live — missing/ok/stale/conflict cases pass; bugfix for set -e glob failure in preflight |
