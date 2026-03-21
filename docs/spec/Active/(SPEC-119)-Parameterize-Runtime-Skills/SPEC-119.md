---
title: "Parameterize Runtime Skills With swain_trunk()"
artifact: SPEC-119
track: implementation
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
parent-epic: EPIC-029
priority-weight: high
depends-on-artifacts:
  - SPEC-118
linked-artifacts:
  - EPIC-029
  - ADR-013
---

# Parameterize Runtime Skills With swain_trunk()

## Goal

Replace all hardcoded trunk branch references in runtime skill instructions with dynamic detection via `scripts/swain-trunk.sh`.

## Changes

### swain-sync (SKILL.md)
- Add `TRUNK=$(bash "$REPO_ROOT/scripts/swain-trunk.sh")` to Step 1 worktree detection preamble
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
