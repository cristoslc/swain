---
title: "Session Archive Mechanism"
artifact: SPEC-248
track: implementable
status: Proposed
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-056
priority-weight: medium
depends-on-artifacts: []
linked-artifacts: []
---

# SPEC-248: Session Archive Mechanism

## Goal

Implement session.json archival so session state survives worktree deletion. This enables retrospective reconstruction after cleanup.

## Problem

When bin/swain prunes a worktree, the worktree's `.agents/session.json` is deleted. Retro reconstruction requires session data (focus lane, decisions, bookmark history). Without archival, this data is lost.

## Deliverables

A shell script (`.agents/bin/swain-session-archive.sh`) that:
1. Copies session.json from worktree to a central archive before deletion
2. Compresses old archives (>7 days)
3. Provides lookup by session ID or artifact ID

Archive location: `.agents/session-archive/` in the main checkout.

## Acceptance Criteria

- [ ] **AC1: Archive before deletion**
  - `swain-session-archive.sh save <worktree-path>` copies session.json to archive
  - Naming: `<session-id>.json` in `.agents/session-archive/`
  - Fails gracefully if no session.json exists

- [ ] **AC2: Lookup by session ID**
  - `swain-session-archive.sh get <session-id>` returns the archived session.json
  - Returns exit 1 if not found

- [ ] **AC3: Lookup by artifact ID**
  - `swain-session-archive.sh find <artifact-id>` returns all sessions that touched the artifact
  - Searches focus_lane and bookmark fields

- [ ] **AC4: Compression**
  - Archives older than 7 days are gzipped
  - Lookup still works on compressed archives

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-04 | -- | Materialized for EPIC-056 |
