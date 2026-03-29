---
title: "Doctor bin/ Auto-Repair"
artifact: SPEC-188
track: implementation
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
parent-epic: EPIC-047
priority-weight: medium
depends-on-artifacts:
  - SPEC-186
linked-artifacts:
  - ADR-019
  - SPEC-067
  - SPEC-180
---

# Doctor bin/ Auto-Repair

## Goal

swain-doctor detects missing or broken `bin/` symlinks for operator-facing scripts and auto-repairs them. Mirrors the `.agents/bin/` convention (SPEC-186) for operator-facing scripts.

## Behavior

### Registry

Operator-facing scripts are explicitly registered (not auto-discovered). Initial registry:

| Script | Canonical location | Status |
|--------|--------------------|--------|
| `swain-box` | `skills/swain/scripts/swain-box` | Existing (SPEC-067) |
| `swain` | `skills/swain/scripts/swain` | Future (SPEC-180) |

### Health check per script

For each registered script, check `bin/<script-name>`:

| Status | Condition | Action |
|--------|-----------|--------|
| **ok** | Symlink exists and resolves to the correct skill-tree target | Silent |
| **missing** | No file at `bin/<script-name>` | Create `bin/` if needed, create symlink, report "repaired" |
| **stale** | Symlink exists but points to wrong target | Update symlink, report "repaired (stale)" |
| **conflict** | A real file (not a symlink) exists | Warn with manual remediation instructions |

### Symlink creation

```bash
mkdir -p bin
ln -sf "../skills/<skill>/scripts/<script-name>" "bin/<script-name>"
```

### Backward compatibility

If a root symlink exists at `./<script-name>` (old convention), migrate it:
1. Remove the old root symlink
2. Create the new `bin/<script-name>` symlink
3. Report "migrated from ./<script-name> to bin/<script-name>"

## Deliverables

- Updated `swain-doctor/SKILL.md` — new health check section for `bin/`
- Updated `swain-preflight.sh` — check `bin/` symlinks

## Test Plan

- T1: Doctor on a repo with no `bin/` — directory created, symlinks populated for installed scripts
- T2: Doctor on a repo with old root symlink `./swain-box` — migrated to `bin/swain-box`
- T3: Doctor on a repo with correct `bin/swain-box` — silent pass

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Created as EPIC-047 child |
