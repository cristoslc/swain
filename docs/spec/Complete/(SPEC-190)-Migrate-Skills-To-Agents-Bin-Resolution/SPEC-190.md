---
title: "Migrate All Skills to .agents/bin/ Resolution"
artifact: SPEC-190
track: implementation
status: Complete
author: cristos
created: 2026-03-29
last-updated: 2026-03-29
parent-epic: EPIC-047
priority-weight: medium
depends-on-artifacts:
  - SPEC-186
linked-artifacts:
  - ADR-019
---

# Migrate All Skills to .agents/bin/ Resolution

## Goal

Replace all `find ... -path '*/scripts/<name>' -print -quit` patterns in swain skill SKILL.md files with direct `.agents/bin/<name>` resolution, per ADR-019's agent-facing script convention.

## Context

There are ~55 `find`-based script lookups across 14 swain skills, referencing 24 unique scripts. Each invocation does a filesystem traversal that is slow and fragile. With SPEC-186 ensuring `.agents/bin/` symlinks are auto-repaired by the preflight, skills can resolve scripts in O(1) via `$REPO_ROOT/.agents/bin/<script-name>`.

## Scope

Every `skills/swain-*/SKILL.md` file that contains a `find ... -path '*/scripts/<name>' -print -quit` pattern.

### Skills to update (14)

| Skill | find invocations | Scripts referenced |
|-------|------------------|--------------------|
| swain-session | 13 | swain-session-bootstrap.sh, swain-session-state.sh, swain-session-check.sh, swain-worktree-name.sh, swain-focus.sh, swain-status.sh, swain-tab-name.sh, swain-bookmark.sh, chart.sh |
| swain-design | 9 | swain-session-check.sh, chart.sh, resolve-artifact-link.sh, adr-check.sh, specwatch.sh, design-check.sh, swain-bookmark.sh |
| swain-sync | 7 | swain-session-check.sh, adr-check.sh, design-check.sh, detect-duplicate-numbers.sh, rebuild-index.sh, swain-bookmark.sh |
| swain-do | 5 | swain-session-check.sh, chart.sh, swain-bookmark.sh, swain-tab-name.sh, ingest-plan.py |
| swain-retro | 5 | swain-session-check.sh, chart.sh, resolve-artifact-link.sh, swain-bookmark.sh |
| swain-release | 3 | swain-session-check.sh, security-scan.sh, swain-bookmark.sh |
| swain-security-check | 3 | swain-session-check.sh, security_check.py |
| swain-roadmap | 3 | swain-session-check.sh, chart.sh, swain-focus.sh |
| swain-keys | 2 | swain-keys.sh, swain-bookmark.sh |
| swain-doctor | 2 | swain-box (operator — `bin/`), migrate-to-troves.sh |
| swain-init | 1 | swain-box (operator — `bin/`) |

### Scripts referenced (24 unique)

```
adr-check.sh          chart.sh               design-check.sh
detect-duplicate-numbers.sh  ingest-plan.py    migrate-to-troves.sh
rebuild-index.sh       render_changelog.py    resolve-artifact-link.sh
resolve-proxy.sh       security_check.py      security-scan.sh
specwatch.sh           swain-bookmark.sh      swain-focus.sh
swain-keys.sh          swain-preflight.sh     swain-session-bootstrap.sh
swain-session-check.sh swain-session-state.sh swain-status.sh
swain-tab-name.sh      swain-worktree-name.sh migrate-to-trunk-release.sh
```

## Replacement pattern

**Before:**
```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)" build
```

**After:**
```bash
bash "$REPO_ROOT/.agents/bin/chart.sh" build
```

Where `REPO_ROOT` is set once at the top of each skill's preamble (most skills already do this).

### Operator-facing scripts

References to operator-facing scripts (`swain-box`, `swain`) should resolve via `bin/` instead of `.agents/bin/`:

```bash
bin/swain-box
```

### Edge case: swain-init

swain-init runs before `.agents/bin/` exists (it creates it in Step 6.1.1). Init's own `find` patterns are acceptable — they bootstrap the convention. No change needed for swain-init.

## Deliverables

- Updated SKILL.md for all 14 skills listed above
- No `find ... -path '*/scripts/<name>' -print -quit` patterns remain in any SKILL.md (except swain-init bootstrap)

## Test Plan

- T1: Grep all `skills/swain-*/SKILL.md` for `find.*scripts.*-print` — zero matches (excluding swain-init)
- T2: Run preflight — no errors from missing scripts
- T3: Spot-check 3 skills (swain-session, swain-sync, swain-design) — script references resolve correctly

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-29 | — | Created as EPIC-047 child; ~55 replacements across 14 skills |
| Complete | 2026-03-29 | — | All 11 skills use .agents/bin/ resolution (64 references); zero find patterns remain outside swain-init bootstrap; all 3 test cases pass |
