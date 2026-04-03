---
title: "Bookmark Creation During Worktree Lifecycle"
artifact: SPEC-235
track: implementable
status: Proposed
author: cristos
created: 2026-04-02
priority-weight: medium
type: enhancement
parent-epic: EPIC-055
swain-do: required
---

# Bookmark Creation During Worktree Lifecycle

## The Problem Statement Section.

Session bookmarks are not created when worktrees are added. swain-session creates worktrees via swain-do dispatch (SPEC-195) but does not create a corresponding bookmark. Every worktree added during a session starts as an orphan. swain-teardown correctly identifies orphan worktrees but cannot fix the root cause: no bookmark was created at creation time.

Additionally, swain-bookmark.sh and session-bookmark.sh were separate concerns. swain-bookmark.sh managed context notes in session.json while session-bookmark.sh managed worktree records in bookmarks.txt. Two files tracking bookmarks created unnecessary complexity. The solution unifies both into session.json.

## The Desired Outcomes Section.

Every worktree created during a session has a corresponding bookmark created at the same time. The worktree path, branch name, session_id, and timestamp are recorded in session.json. When a worktree is removed, its bookmark entry is removed. swain-teardown finds zero orphan worktrees after every session close. Bookmarks are a reliable record of which worktrees belong to which sessions.

swain-bookmark.sh is the single tool for all bookmark management. It handles both context notes and worktree records. There is no separate bookmarks.txt file.

## The External Behavior Section.

### The Unified Session Schema Sub-section.

session.json gains a `worktrees` array. The full schema becomes:

```json
{
  "lastBranch": "trunk",
  "lastContext": "Working on swain-session skill",
  "preferences": { "verbosity": "concise" },
  "bookmark": {
    "note": "Left off implementing the bootstrap script",
    "files": ["SKILL.md"],
    "timestamp": "2026-03-10T14:32:00Z"
  },
  "worktrees": [
    {
      "path": "/path/to/worktree",
      "branch": "spec-174-branch-collision",
      "session_id": "session-20260402-001",
      "last_active": "2026-04-02T10:30:00Z"
    }
  ]
}
```

The worktrees array is managed exclusively by swain-bookmark.sh worktree subcommands.

### The Bookmark Entry Format Sub-section.

Each worktree bookmark is a JSON object in the session.json worktrees array. Fields:

| Field | Type | Description |
|-------|------|-------------|
| path | string | Absolute path to the worktree directory |
| branch | string | Current branch name in the worktree |
| session_id | string | Session ID that created or last touched this worktree |
| last_active | string | ISO-8601 timestamp of last activity in this worktree |

The path is the unique key. Duplicate paths are updated, not appended.

### The swain-bookmark.sh Interface Sub-section.

swain-bookmark.sh gains worktree subcommands while preserving existing behavior:

```
swain-bookmark.sh "context note text"         # existing: set context note
swain-bookmark.sh --clear                      # existing: clear context note
swain-bookmark.sh worktree add <path> <branch> # new: add or update worktree bookmark
swain-bookmark.sh worktree remove <path>       # new: remove worktree bookmark
swain-bookmark.sh worktree list                # new: list all worktree bookmarks
swain-bookmark.sh worktree prune               # new: remove stale worktree entries
```

The worktree subcommands require jq. If jq is unavailable, they fail with a clear message.

## The Acceptance Criteria Section.

AC1 establishes that worktree bookmarks are created when worktrees are added. When swain-do creates a worktree during an active session, swain-bookmark.sh worktree add is called with the worktree path and branch name. The entry is stored in session.json worktrees array with the current session_id and timestamp.

AC2 establishes that duplicate worktrees are updated, not appended. If a worktree path already exists in the worktrees array, its branch, session_id, and last_active fields are updated to the new values. There is exactly one entry per unique path.

AC3 establishes that worktree bookmarks are removed when worktrees are deleted. When swain-bookmark.sh worktree remove is called with a path, that entry is removed from the worktrees array. This runs after git worktree remove succeeds.

AC4 establishes that trunk is never bookmarked. When a worktree path equals the repo root, swain-bookmark.sh worktree add returns early without writing. The trunk worktree is the base context, not a session worktree.

AC5 establishes that swain-teardown uses session.json as the worktree bookmark source. The orphan worktree check reads from session.json worktrees array, not bookmarks.txt. The bookmarks.txt file is no longer created or read by any swain skill.

## The Verification Section.

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | Manual: create worktree during session, verify entry in session.json worktrees array | |
| AC2 | Manual: create same worktree twice, verify only one entry with updated timestamp | |
| AC3 | Manual: remove worktree, verify entry removed from session.json | |
| AC4 | Manual: start session on trunk, verify no trunk entry in worktrees array | |
| AC5 | Manual: run teardown, verify it reads from session.json not bookmarks.txt | |

## The Scope and Constraints Section.

### The In Scope Items Sub-section.

| Item | Description |
|------|-------------|
| Unified session.json schema | worktrees array alongside existing bookmark and preferences fields |
| swain-bookmark.sh worktree subcommands | add, remove, list, prune operations on worktrees array |
| Worktree creation integration | swain-do calls swain-bookmark.sh after worktree creation |
| Worktree removal integration | swain-teardown calls swain-bookmark.sh after git worktree remove |
| bookmarks.txt retirement | No new bookmarks.txt created; existing files become stale |

### The Out of Scope Items Sub-section.

| Item | Rationale |
|------|-----------|
| bookmarks.txt migration | Existing bookmarks.txt entries are a one-time migration; separate task |
| Multi-session worktree sharing | Not applicable — a worktree belongs to one session at a time |
| jq dependency removal | jq is the standard swain JSON tool; no need to avoid it |

## The Implementation Approach Section.

### The swain-bookmark.sh Enhancement Sub-section.

Extend swain-bookmark.sh to detect and dispatch worktree subcommands. Parse arguments in order: if first arg is "worktree", dispatch to worktree handler. Otherwise, use existing note/clear behavior.

```bash
# Detect worktree subcommand
if [[ "${1:-}" == "worktree" ]]; then
  shift
  case "${1:-}" in
    add)    cmd_worktree_add "$2" "$3" ;;
    remove) cmd_worktree_remove "$2" ;;
    list)   cmd_worktree_list ;;
    prune)  cmd_worktree_prune ;;
    *)      echo "Usage: swain-bookmark.sh worktree <add|remove|list|prune>" >&2; exit 1 ;;
  esac
  exit $?
fi
```

The worktree_add function: read existing worktrees from session.json, filter by path (grep -v to temp), append updated entry, write back.

The worktree_remove function: filter out the path entry, write back.

The worktree_list function: read worktrees array, print each entry as a line.

The worktree_prune function: remove entries whose path directories no longer exist.

### The Worktree Creation Integration Sub-section.

In the swain-do worktree creation preamble, replace the session-bookmark.sh call with swain-bookmark.sh:

```bash
WT_PATH="$(pwd)"
WT_BRANCH="$(git branch --show-current 2>/dev/null || echo 'unknown')"
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree add "$WT_PATH" "$WT_BRANCH"
```

### The Worktree Removal Integration Sub-section.

In the teardown orphan removal flow, replace the session-bookmark.sh call with swain-bookmark.sh:

```bash
git worktree remove "$wt_path" 2>/dev/null && \
  bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" worktree remove "$wt_path" && \
  removed_worktrees+=("$wt_path ($wt_branch)")
```

## The Lifecycle Section.

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | | Initial spec |
