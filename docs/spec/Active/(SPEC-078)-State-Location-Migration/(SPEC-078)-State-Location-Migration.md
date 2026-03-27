---
title: "State location migration"
artifact: SPEC-078
track: implementable
status: Active
author: cristos
created: 2026-03-18
last-updated: 2026-03-18
type: enhancement
parent-epic: EPIC-031
linked-artifacts: []
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# State location migration

## Problem Statement

swain-status writes its cache to `~/.claude/projects/<slug>/memory/status-cache.json` — the old global Claude memory location. swain-session and swain-stage have already migrated to `.agents/` (project-local, version-controlled). This split means two sources of truth for project state, and the global location won't work correctly in multi-project Claude Code sessions or when the project slug changes.

## External Behavior

All swain runtime state files live in `.agents/` within the project root:
- `status-cache.json` → `.agents/status-cache.json`
- `stage-status.json` → `.agents/stage-status.json` (verify current location)

The old `~/.claude/projects/<slug>/memory/` paths are not used for any swain state.

## Acceptance Criteria

**AC-1:** swain-status reads/writes its cache to `.agents/status-cache.json`.

**AC-2:** If old cache exists at `~/.claude/projects/<slug>/memory/status-cache.json`, it is read once as fallback on first access, then `.agents/` is used going forward.

**AC-3:** swain-stage's `stage-status.json` location is documented in its SKILL.md (currently undocumented).

**AC-4:** swain-retro's memory file path uses a documented discovery mechanism rather than assuming the `~/.claude/` slug.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC-1 | Grep swain-status SKILL.md for cache path | |
| AC-2 | Review migration/fallback logic | |
| AC-3 | Read swain-stage SKILL.md for path documentation | |
| AC-4 | Read swain-retro SKILL.md for memory path | |

## Scope & Constraints

**In scope:** SKILL.md changes for swain-status, swain-stage, swain-retro. Script changes to `swain-status.sh` if it hardcodes the path.

**Out of scope:** Migrating the Claude Code memory system itself. Only swain's own state files.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-18 | — | Created from audit theme #5: state location divergence |
