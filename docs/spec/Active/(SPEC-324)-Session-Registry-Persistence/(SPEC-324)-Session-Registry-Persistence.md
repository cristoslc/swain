---
title: "Session Registry Persistence"
artifact: SPEC-324
track: implementable
status: Active
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
priority-weight: high
type: feature
parent-epic: EPIC-071
parent-initiative: ""
linked-artifacts:
  - ADR-046
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Session Registry Persistence

## Problem Statement

Session state is in-memory only. Bridge restarts lose all session tracking. When the bridge process restarts (due to crash, maintenance, or system reboot), it has no memory of which sessions it created, which worktrees they serve, or what state they were in. This forces manual cleanup and re-creation of sessions after every restart.

## Desired Outcomes

A persistent session registry on disk that survives bridge restarts. On startup, the bridge reads the registry and reconciles it with live opencode serve sessions, cleaning up orphaned entries and resuming tracking of valid ones.

## External Behavior

**Registry path:** `<project-root>/.swain/swain-helm/session-registry.json`

**Key:** Worktree branch name (the Zulip topic) — not session_id.

**Entry schema per branch:**
- `opencode_session_id`
- `state`
- `topic`
- `worktree_path`
- `artifact`
- `started_at`
- `last_activity`

**Writes:** Every state change (session created, state updated, session ended).

**Startup reconciliation:**
1. Read registry from disk.
2. Call `POST /session list` on opencode serve to get live sessions.
3. For each registry entry with no matching live session, delete the entry.
4. For each live session with no registry entry, it is an orphan from another source — leave it alone.

## Acceptance Criteria

1. **Given** a session state changes, **when** the change occurs, **then** the registry is written to `<project-root>/.swain/swain-helm/session-registry.json`.

2. **Given** the registry file, **when** it is read, **then** entries are keyed by worktree branch name (the Zulip topic), not by session_id.

3. **Given** a registry entry, **when** it is written, **then** it contains `opencode_session_id`, `state`, `topic`, `worktree_path`, `artifact`, `started_at`, and `last_activity`.

4. **Given** the bridge starts up, **when** it reads the registry, **then** it reconciles with opencode serve sessions by calling session list and deleting orphaned entries.

5. **Given** dead entries (process dead, no worktree), **when** startup reconciliation runs, **then** they are cleaned up from the registry.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~80 lines of Python.
- JSON file I/O — no database, no SQLite.
- Reconciliation is one-directional: registry entries without live sessions are deleted. Orphaned live sessions from other sources are not touched.
- The registry is per-project (lives under `<project-root>`).
- No locking on the JSON file — only one bridge writes per project.
- `last_activity` is updated on every state transition, not on every poll cycle.

## Implementation Approach

1. Write a `SessionRegistry` class with `read()`, `write()`, `update_entry()`, and `delete_entry()` methods.
2. `update_entry()` takes a branch name and merges the provided fields into the entry, then writes.
3. `write()` serializes the full dict to JSON with atomic write (write to tmp, rename).
4. Write a `reconcile()` method that calls opencode serve's session list, compares with registry, and deletes entries whose session_id is not in the live list.
5. Add dead-entry cleanup: check if worktree path still exists and if process is alive.
6. Wire `update_entry()` into every session state change in ProjectBridge.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |