---
title: "Continuous Worktree Discovery"
artifact: SPEC-323
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

# Continuous Worktree Discovery

## Problem Statement

Worktrees are created after the bridge starts. The bridge must discover them continuously. Currently the bridge has no mechanism to detect new or removed worktrees; it only knows about worktrees that existed at startup. This means sessions for new worktrees are never created, and sessions for removed worktrees are never cleaned up.

## Desired Outcomes

ProjectBridge polls `git worktree list` on a configurable interval and acts on diffs: new worktrees get sessions, removed worktrees get cleaned up, and trunk always has a session. The bridge only acts on changes, not on the full list each cycle.

## External Behavior

**Poll interval:** 15s default, configurable via `worktree_poll_interval_s` in project config.

**New worktree detected:**
1. Derive topic from branch name.
2. Create opencode session via the opencode adapter.
3. Announce in control topic.

**Removed worktree detected:**
1. Abort session (`POST /session/{id}/abort`).
2. Export session data.
3. Mark dead in registry.
4. Announce in control topic.

**Trunk handling:** Always has a session with topic "trunk".

**Diff detection:** Compare current `git worktree list --porcelain` output to cached set. Only act on changes.

## Acceptance Criteria

1. **Given** ProjectBridge is running, **when** it polls `git worktree list --porcelain`, **then** it does so every 15s (configurable via `worktree_poll_interval_s`).

2. **Given** a new worktree is detected, **when** the diff is computed, **then** ProjectBridge derives a topic from the branch name, creates an opencode session, and announces it in the control topic.

3. **Given** a worktree is removed, **when** the diff is computed, **then** ProjectBridge aborts the session via `POST /session/{id}/abort`, exports session data, marks it dead, and announces in the control topic.

4. **Given** a worktree already has a session, **when** that worktree appears in the worktree list, **then** follow-up commands are sent to the existing session instead of creating a new one.

5. **Given** the trunk branch, **when** ProjectBridge starts, **then** a session is created with topic "trunk".

6. **Given** the worktree list has not changed, **when** a poll cycle runs, **then** no actions are taken (diff is empty).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- ~100 lines of Python.
- `git worktree list --porcelain` is the sole discovery mechanism.
- Branch name to topic mapping: trunk → "trunk", others → branch name directly (no sanitization in this spec).
- Session creation and abort are delegated to the opencode adapter (SPEC-322).
- This spec does not define what "announce in control topic" contains — that is UI/UX detail.
- No debouncing — if worktrees change rapidly between polls, each cycle acts on the diff.

## Implementation Approach

1. Write a `WorktreeScanner` class with a `poll()` method.
2. `poll()` runs `git worktree list --porcelain`, parses output into a set of (path, branch) tuples.
3. Diff current set against cached `_last_known` set to get added/removed.
4. For added: derive topic, call opencode adapter to create session, announce.
5. For removed: call opencode adapter to abort session, export data, mark dead, announce.
6. Update `_last_known` after processing.
7. Ensure trunk session exists on first poll.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-18 | -- | Initial creation |