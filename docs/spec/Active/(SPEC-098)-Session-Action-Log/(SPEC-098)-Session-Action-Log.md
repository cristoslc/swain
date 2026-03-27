---
title: "Session Action Log"
artifact: SPEC-098
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: feature
parent-epic: EPIC-036
parent-initiative: ""
linked-artifacts:
  - EPIC-016
  - SPEC-094
  - SPEC-099
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Session Action Log

## Problem Statement

The current session bookmark (`session.json .bookmark`) is a point-in-time marker — it records the last push note and timestamp. Skills that perform state-changing operations (artifact transitions, task completions, file edits) leave no structured trace of what they did. When swain-sync runs, it sees only a flat `git diff` with no way to attribute file changes to the logical actions that produced them.

Critically, multiple swain sessions can operate concurrently on the same worktree/branch — an operator session and a dispatched background agent, or two terminal tabs working the same branch. Today there is no mechanism to distinguish which session produced which changes. Whichever session runs swain-sync last silently absorbs the other's work into its commit.

This spec extends session.json with a **session-scoped action log** — an append-only event stream keyed by session ID that skills emit into as they operate. Each session's actions are namespaced so concurrent sessions can write to the same file without clobbering each other. Downstream consumers (primarily swain-sync, SPEC-099) read only their own session's actions when producing commits.

## External Behavior

### Schema

A new top-level `action_log` object in session.json, keyed by session ID:

```json
{
  "bookmark": { "note": "...", "timestamp": "..." },
  "action_log": {
    "s_a1b2c3": {
      "started": "2026-03-19T14:00:00Z",
      "actions": [
        {
          "id": "act_001",
          "type": "artifact-transition",
          "timestamp": "2026-03-19T14:30:00Z",
          "summary": "SPEC-094 Active -> Complete",
          "files": [
            "docs/spec/Complete/(SPEC-094)-Frontmatter-Schema/..."
          ],
          "artifact": "SPEC-094",
          "commit_prefix": "docs"
        }
      ]
    },
    "s_d4e5f6": {
      "started": "2026-03-19T14:15:00Z",
      "actions": [
        {
          "id": "act_002",
          "type": "script-change",
          "timestamp": "2026-03-19T14:35:00Z",
          "summary": "Fix path resolution in design-check.sh",
          "files": [
            "skills/swain-design/scripts/design-check.sh"
          ],
          "commit_prefix": "fix"
        }
      ]
    }
  }
}
```

### Session identity

Each swain session gets a stable ID (`s_` + 6-char hex) generated at session start (by swain-session) and stored in the `SWAIN_SESSION_ID` environment variable. All action log operations use this ID as the namespace key. If `SWAIN_SESSION_ID` is unset, the action API generates a transient ID and warns — this ensures backward compatibility but signals misconfiguration.
```

### Action types

| Type | Emitted by | Typical commit_prefix |
|------|-----------|----------------------|
| `artifact-create` | swain-design | `docs` |
| `artifact-transition` | swain-design | `docs` |
| `task-complete` | swain-do | `feat` or `fix` (from task context) |
| `index-rebuild` | swain-sync, swain-design | `chore` |
| `script-change` | manual / agent edits | `fix`, `feat`, or `refactor` |
| `config-change` | swain-doctor, swain-init | `chore` |

### API (swain-bookmark.sh extension)

All action operations require `SWAIN_SESSION_ID` (or accept `--session-id` override).

```bash
# Append an action to the current session's log
swain-bookmark.sh --action \
  --type artifact-transition \
  --summary "SPEC-094 Active -> Complete" \
  --files docs/spec/Complete/... \
  --artifact SPEC-094 \
  --commit-prefix docs

# Read only the current session's actions
swain-bookmark.sh --read-actions

# Read a specific session's actions
swain-bookmark.sh --read-actions --session-id s_a1b2c3

# Clear only the current session's actions (after successful push)
swain-bookmark.sh --clear-actions

# List all session IDs with action counts (diagnostic)
swain-bookmark.sh --list-sessions
```

### Constraints

- **Session-scoped:** each session's actions live under `action_log.<session_id>`. Sessions never read or write other sessions' action arrays.
- **Append-only during session:** actions within a session are only appended, never edited or reordered.
- **Cleared per-session on push:** swain-sync clears only `action_log.<own_session_id>` after all commits succeed. Other sessions' entries are untouched. If push fails, log is preserved for retry.
- **Concurrent-safe writes:** use jq atomic read-modify-write (write to `.tmp`, then `mv`) with flock if available. Two sessions appending simultaneously must not lose data. On macOS (no flock), the `.tmp` + `mv` pattern provides sufficient atomicity for the expected concurrency level (2-3 sessions, not hundreds).
- **File paths are relative** to repo root (consistent with git).
- **Session ID generation:** `s_` + 6-char hex from `head -c 3 /dev/urandom | xxd -p`. Generated once at session start by swain-session, exported as `SWAIN_SESSION_ID`.
- **Action ID generation:** `act_` + 6-char hex, unique within a session.
- **Maximum log size per session:** if a session's `actions` exceeds 100 entries, oldest entries are dropped on append (ring buffer).
- **Stale session cleanup:** `--clear-actions --stale` removes action_log entries whose `started` timestamp is older than 24 hours. swain-doctor can call this periodically.
- **Backward compatible:** session.json without `action_log` key is valid; consumers treat missing key as empty object (no sessions, no actions).

## Acceptance Criteria

- **Given** a skill performs an artifact transition with `SWAIN_SESSION_ID=s_abc123`, **when** it calls `swain-bookmark.sh --action`, **then** the action appears in `session.json .action_log.s_abc123.actions[]` with correct type, summary, files, and timestamp.
- **Given** session.json has no `action_log` key, **when** `--action` is called, **then** `action_log.<session_id>` is created with a `started` timestamp and single-element `actions` array.
- **Given** two sessions (s_aaa, s_bbb) both append actions, **when** `--read-actions` is called by session s_aaa, **then** only s_aaa's actions are returned.
- **Given** session s_aaa has actions and session s_bbb has actions, **when** s_aaa calls `--clear-actions`, **then** `action_log.s_aaa` is removed but `action_log.s_bbb` is untouched.
- **Given** an old session.json without `action_log`, **when** any non-action bookmark operation is performed, **then** it works unchanged (no regression).
- **Given** 100 actions already exist for a session, **when** a 101st is appended, **then** the oldest action in that session is dropped.
- **Given** `SWAIN_SESSION_ID` is unset, **when** `--action` is called, **then** a transient session ID is generated and a warning is emitted to stderr.
- **Given** action_log entries older than 24 hours exist, **when** `--clear-actions --stale` is called, **then** those entries are removed regardless of session ID.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Does NOT change the bookmark write/read/clear behavior — those paths are untouched.
- Does NOT require EPIC-016 (worktree-aware bookmarks) to be complete, but schema additions must not conflict with the planned `worktree` field.
- The `commit_prefix` field is a **suggestion** — SPEC-099's commit atomization may override based on file-level heuristics.
- Skills are responsible for emitting their own actions. This spec defines the log format and append API, not the emission points in each skill (those are implementation details of SPEC-099 integration).

## Implementation Approach

1. **Session ID provisioning in swain-session** — generate `SWAIN_SESSION_ID` at session start, export it so all child processes inherit it. Store in session.json alongside other session state.
2. **Extend swain-bookmark.sh** with `--action`, `--read-actions`, `--clear-actions`, and `--list-sessions` flags. All action operations read `SWAIN_SESSION_ID` (with `--session-id` override). Use jq atomic read-modify-write (`.tmp` + `mv`) for concurrent safety.
3. **Add action schema validation** — a simple jq filter that checks required fields (type, summary, files, timestamp) on append.
4. **Test concurrent safety** — two shells appending actions in a tight loop to the same session.json, verify no data loss.
5. **Test session isolation** — verify `--read-actions` and `--clear-actions` respect session boundaries.
6. **Emit actions from swain-design** — artifact creation and phase transitions are the highest-value emission points.
7. **Emit actions from swain-do** — task completion events.
8. **Wire stale cleanup into swain-doctor** — `--clear-actions --stale` on health check runs.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Initial creation |
