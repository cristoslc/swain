---
title: "Preflight Self-Healing Compliance Audit"
artifact: SPEC-191
track: implementation
status: Active
author: cristos
created: 2026-03-29
last-updated: 2026-03-29
parent-epic: ""
priority-weight: medium
depends-on-artifacts:
  - ADR-020
linked-artifacts:
  - ADR-020
  - SPEC-186
  - SPEC-188
---

# Preflight Self-Healing Compliance Audit

## Goal

Audit all existing preflight checks against ADR-020's self-healing convention. Checks that can safely self-heal but currently only report should be updated to auto-repair.

## Current checks inventory

From `swain-preflight.sh`, each check classified per ADR-020:

| # | Check | Current behavior | Can self-heal? | Action |
|---|-------|-----------------|---------------|--------|
| 1 | No governance file (AGENTS.md/CLAUDE.md) | Report | No — operator must choose which to create | Keep |
| 2 | Governance markers missing | Report | No — content is operator-authored | Keep |
| 3 | Governance block stale | Report | No — operator may have intentional differences | Keep |
| 4 | `.agents/` directory missing | Report | **Yes** — `mkdir -p .agents` | **Update** |
| 5 | Invalid ticket frontmatter | Report | No — requires understanding of ticket intent | Keep |
| 6 | Stale `.beads/` directory | Report | No — migration script needs operator review | Keep |
| 7 | `docs/evidence-pools/` detected | Report | No — trove migration needs operator review | Keep |
| 8 | Stale tk lock files | Report | **Yes** — locks older than threshold are safe to remove | **Update** |
| 9 | Old lifecycle directories | Report | No — migration script modifies artifact files | Keep |
| 10 | Commit signing not configured | Report | No — modifies global git config | Keep |
| 11 | Scripts missing executable permission | Report | **Yes** — `chmod +x` is safe and idempotent | **Update** |
| 12 | Skill change detection (trunk) | Report | No — requires operator judgment on branching | Keep |
| 13 | `.agents/bin/` symlinks | **Self-heals** | Already compliant (SPEC-186) | Done |
| 14 | `bin/` symlinks | **Self-heals** | Already compliant (SPEC-188) | Done |
| 15 | `.agents/bin/swain-trunk.sh` missing | Report | No — self-heal covers this via #13; this fires only if no script exists in skill tree | Keep |
| 16 | swain-trunk.sh returned empty | Report | No — indicates a git state problem | Keep |
| 17 | Real file at symlink path | Report | No — could destroy operator work | Keep |

## Deliverables

Update `swain-preflight.sh` for the three checks marked **Update**:

### Check 4: `.agents/` directory missing
```bash
# Before: issues+=(".agents directory missing")
# After: self-heal
mkdir -p .agents
echo "advisory: created .agents/ directory"
```

### Check 8: Stale tk lock files
```bash
# Before: issues+=("stale tk lock files in .tickets/.locks/")
# After: remove locks older than 1 hour
find .tickets/.locks/ -type d -mmin +60 -exec rm -rf {} + 2>/dev/null
echo "advisory: removed stale tk lock files"
```

### Check 11: Scripts missing executable permission
```bash
# Before: issues+=("scripts missing executable permission")
# After: chmod +x
chmod +x <scripts>
echo "advisory: fixed executable permissions on N scripts"
```

## Test Plan

- T1: Remove `.agents/` — preflight recreates it, no issue reported
- T2: Create a stale lock file (>1h old) — preflight removes it
- T3: Remove +x from a skill script — preflight restores it
- T4: All three self-heal on first run, clean on second run

## Acceptance Criteria

- Zero checks in `swain-preflight.sh` that report-only when ADR-020 says they should self-heal
- Each self-healing check emits an advisory line
- The classification table in this spec matches the actual code

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-29 | — | Surfaced during RETRO-2026-03-29-adr-019-script-convention |
