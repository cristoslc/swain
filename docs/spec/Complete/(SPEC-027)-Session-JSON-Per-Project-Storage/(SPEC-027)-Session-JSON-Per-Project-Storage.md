---
title: "Session JSON Per-Project Storage"
artifact: SPEC-027
track: implementable
status: Complete
type: bug
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
source-issue: "github:cristoslc/swain#40"
parent-epic: ""
swain-do: required
addresses: []
linked-artifacts: []
depends-on-artifacts: []
implementation-commits: 4020504
---

# Session JSON Per-Project Storage

## Problem Statement

`swain-session` stores `session.json` at `~/.claude/projects/<project-path-slug>/memory/session.json` — Claude Code's global memory directory scoped by project path slug. This causes:

- **Cross-project leakage**: Bookmarks from one project appear in another (observed: persona briefing bookmark from a different project appeared in HouseOps session restore)
- **Invisible state**: Session state is outside the repo, invisible to collaborators, not version-controlled
- **Principle violation**: Project-specific state should live in the project

Source: [GitHub Issue #40](https://github.com/cristoslc/swain/issues/40)

## Acceptance Criteria

1. `session.json` is stored at `<project-root>/.agents/session.json` instead of the global Claude memory directory
2. `swain-bookmark.sh` discovers and writes to `.agents/session.json`
3. `swain-status.sh` reads session data from `.agents/session.json`
4. `swain-session` SKILL.md documents the new location
5. `swain-doctor` runtime-checks.md no longer lists session.json as a memory directory file
6. Backward compatibility: if `.agents/session.json` doesn't exist but the old global path does, migrate it

## Scope

In scope:
- Move session.json storage from global memory dir to `.agents/session.json`
- Update all readers/writers: swain-bookmark.sh, swain-status.sh, swain-session SKILL.md
- Update swain-doctor runtime-checks reference
- One-time migration from old location

Out of scope:
- Moving status-cache.json or stage-status.json (these are caches, not project state)
- Changing session.json schema
- Changing other skills' storage patterns

## Verification

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | session.json stored at .agents/session.json | PASS | swain-bookmark.sh line 18 |
| 2 | swain-bookmark.sh writes to .agents/session.json | PASS | swain-bookmark.sh path discovery updated |
| 3 | swain-status.sh reads from .agents/session.json | PASS | swain-status.sh SESSION_FILE updated |
| 4 | SKILL.md documents new location | PASS | swain-session SKILL.md updated |
| 5 | runtime-checks.md updated | PASS | session.json removed from memory dir list |
| 6 | Backward migration from old path | PASS | swain-bookmark.sh migration logic added |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Complete | 2026-03-13 | 4020504 | Bug fix — direct to Complete per phase skipping |
