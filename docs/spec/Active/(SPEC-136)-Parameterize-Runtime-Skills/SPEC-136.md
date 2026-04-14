---
title: "Parameterize Runtime Skills With swain_trunk()"
artifact: SPEC-136
track: implementation
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
parent-epic: EPIC-029
priority-weight: high
depends-on-artifacts:
  - SPEC-147
linked-artifacts:
  - EPIC-029
  - ADR-013
  - ADR-019
---

# Parameterize Runtime Skills With swain_trunk()

## Goal

Replace all hardcoded trunk branch references in runtime skill instructions with dynamic detection via `swain-trunk.sh` (resolved per [ADR-019](../../../adr/Superseded/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md) agent-facing convention).

## Changes

### swain-sync (SKILL.md)
- Add `TRUNK=$(bash "$REPO_ROOT/.agents/bin/swain-trunk.sh")` to Step 1 worktree detection preamble
- Replace `origin/trunk` merge target with `origin/$TRUNK` (2 occurrences)
- Replace `HEAD:trunk` push target with `HEAD:$TRUNK`
- Replace `--base trunk` PR fallback with `--base "$TRUNK"`

### swain-doctor (SKILL.md)
- Add trunk detection preamble at top of checks
- Replace `origin/trunk` in stale worktree detection with `origin/$TRUNK` (3 occurrences in messages and commands)

### swain-release (SKILL.md)
- Replace hardcoded `trunk` comparisons and checkout/merge with `$TRUNK` variable
- Replace `git push origin trunk` with `git push origin "$TRUNK"`

## Test Plan

- Grep all runtime SKILL.md files for literal `origin/trunk` — zero matches expected (outside comments)
- Verify instructions reference `$TRUNK` variable correctly

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Created as EPIC-029 child |
| Active | 2026-03-28 | — | Updated path to `.agents/bin/swain-trunk.sh` per ADR-019 agent-facing convention |
