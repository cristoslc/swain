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

Session bookmarks are not created when worktrees are added. swain-session creates worktrees via swain-do dispatch (SPEC-195) but does not create a corresponding bookmark in .agents/bookmarks.txt. Every worktree added during a session starts as an orphan. swain-teardown correctly identifies orphan worktrees but cannot fix the root cause: no bookmark was created at creation time. The teardown is a diagnostic tool for a creation-time defect. The creation-time defect is that bookmark creation is not automated in the worktree creation flow.

## The Desired Outcomes Section.

Every worktree created during a session has a corresponding bookmark created at the same time. The worktree path, branch name, and session_id are recorded in bookmarks.txt. When a worktree is removed, its bookmark entry is removed. swain-teardown finds zero orphan worktrees after every session close. Bookmarks are a reliable record of which worktrees belong to which sessions.

## The External Behavior Section.

### The Current Bookmark Creation Sub-section.

swain-session creates worktrees via swain-do. swain-do invokes SPEC-195 worktree creation. SPEC-195 creates the worktree directory and branch but does not update bookmarks.txt. The session creates the worktree. The session does not record the worktree in its bookmarks. Every worktree is an orphan from birth.

### The Desired Bookmark Creation Sub-section.

When a worktree is created during a session, the creating script appends a bookmark entry to bookmarks.txt. The entry contains the worktree path, the branch name, the session_id, and a timestamp. When a worktree is removed, the bookmark entry is removed. The bookmarks.txt file is the session's record of its worktrees.

### The Bookmark Entry Format Sub-section.

Each bookmark is a single line in .agents/bookmarks.txt with pipe-separated fields:

```
<worktree_path>|<branch_name>|<session_id>|<created_timestamp>
```

Example:
```
/Users/cristos/Documents/code/swain/.worktrees/feature-x|/Users/cristos/Documents/code/swain|.session-20260402-001|2026-04-02T10:30:00Z
```

The format is line-oriented and human-readable. Parsing is done with cut or awk.

## The Acceptance Criteria Section.

AC1 establishes that bookmarks are created when worktrees are added. When swain-do creates a worktree during an active session, the creating script appends a bookmark entry to .agents/bookmarks.txt. The bookmark includes the worktree path, branch name, session_id, and timestamp. The session_id is read from session-state.json.

AC2 establishes that duplicate bookmarks are prevented. If a worktree path already has a bookmark entry, the script does not append a duplicate. The existing entry is updated with the new timestamp and session_id instead.

AC3 establishes that bookmarks are cleaned up when worktrees are removed. When a worktree is removed (via git worktree remove or manually), the bookmark entry for that worktree path is removed from bookmarks.txt. The cleanup runs as part of the worktree removal process.

AC4 establishes that trunk is never bookmarked. When a session starts on trunk, no bookmark entry is created for trunk. The trunk worktree is always treated as the base context, not a session worktree. This prevents the trunk worktree from appearing as an orphan.

AC5 establishes that orphan worktrees created before this spec are flagged. When teardown finds a worktree without a bookmark and the bookmark predates this spec's implementation, teardown reports it as a pre-existing orphan with a suggestion to run a migration. The migration is out of scope for this spec.

AC6 establishes that swain-session uses the bookmark file to list session worktrees. The session list command reads bookmarks.txt to show which worktrees belong to the current session. Worktrees without bookmarks are shown as orphan worktrees.

## The Verification Section.

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | Manual: create worktree during session, verify bookmark entry in bookmarks.txt | |
| AC2 | Manual: create same worktree twice, verify only one bookmark entry | |
| AC3 | Manual: remove worktree, verify bookmark entry is removed | |
| AC4 | Manual: start session on trunk, verify trunk has no bookmark | |
| AC5 | Manual: run teardown on pre-existing orphan, verify flag as pre-existing | |
| AC6 | Manual: run session list, verify bookmarks.txt worktrees are shown | |

## The Scope and Constraints Section.

### The In Scope Items Sub-section.

| Item | Description |
|------|-------------|
| Bookmark creation | Append entry to bookmarks.txt on worktree creation |
| Bookmark deduplication | Prevent duplicate entries for same worktree path |
| Bookmark cleanup | Remove entry on worktree removal |
| Trunk exclusion | Never bookmark the trunk worktree |
| Session list integration | Use bookmarks.txt as source of truth for session worktrees |

### The Out of Scope Items Sub-section.

| Item | Rationale |
|------|-----------|
| Bookmark migration for pre-existing orphans | Separate migration spec needed |
| Bookmark garbage collection | Stale bookmarks from closed sessions are a separate concern |
| Distributed bookmarks (multi-repo) | Not applicable to single-repo setup |
| Bookmark sync to remote | No remote bookmark store exists |

## The Implementation Approach Section.

### The Bookmark Creation Script Sub-section.

Create a new script .agents/bin/session-bookmark.sh with add, remove, and list subcommands. The add subcommand creates a bookmark. The remove subcommand deletes a bookmark. The list subcommand shows all bookmarks.

```bash
#!/usr/bin/env bash
# session-bookmark.sh — manage session bookmarks

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BOOKMARK_FILE="$REPO_ROOT/.agents/bookmarks.txt"
SESSION_STATE="$REPO_ROOT/.agents/session-state.json"

add() {
  local wt_path="$1"
  local wt_branch="$2"

  # Skip trunk
  if [ "$wt_path" = "$REPO_ROOT" ]; then
    echo "Skipping trunk — trunk is never bookmarked."
    return 0
  fi

  # Get session_id
  local session_id
  session_id=$(jq -r '.session_id // empty' "$SESSION_STATE" 2>/dev/null)
  if [ -z "$session_id" ]; then
    echo "Warning: No active session — bookmark will not include session_id."
    session_id="no-session"
  fi

  local timestamp
  timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  # Check for existing entry
  if [ -f "$BOOKMARK_FILE" ] && grep -q "^${wt_path}|" "$BOOKMARK_FILE"; then
    # Update existing entry
    sed -i '' "s|^${wt_path}|.*|${wt_path}|${wt_branch}|${session_id}|${timestamp}|" "$BOOKMARK_FILE"
    echo "Updated bookmark: $wt_path"
  else
    # Append new entry
    echo "${wt_path}|${wt_branch}|${session_id}|${timestamp}" >> "$BOOKMARK_FILE"
    echo "Added bookmark: $wt_path"
  fi
}

remove() {
  local wt_path="$1"
  if [ -f "$BOOKMARK_FILE" ]; then
    grep -v "^${wt_path}|" "$BOOKMARK_FILE" > "$BOOKMARK_FILE.tmp" && mv "$BOOKMARK_FILE.tmp" "$BOOKMARK_FILE"
    echo "Removed bookmark: $wt_path"
  fi
}

list() {
  if [ -f "$BOOKMARK_FILE" ]; then
    cat "$BOOKMARK_FILE"
  else
    echo "No bookmarks found."
  fi
}

"$@"
```

### The Worktree Creation Integration Sub-section.

In the worktree creation step of SPEC-195 (swain-do worktree creation flow), call session-bookmark.sh add after the worktree is successfully created. The call happens after git worktree add succeeds and before returning to the operator.

```bash
# After git worktree add succeeds
bash "$REPO_ROOT/.agents/bin/session-bookmark.sh" add "$wt_path" "$wt_branch"
```

### The Worktree Removal Integration Sub-section.

In the teardown worktree removal flow (SPEC-233 step 1b), call session-bookmark.sh remove after git worktree remove succeeds.

```bash
if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
  git worktree remove "$wt_info" 2>/dev/null && \
    bash "$REPO_ROOT/.agents/bin/session-bookmark.sh" remove "$wt_info" && \
    removed_worktrees+=("$wt_info ($wt_branch)")
fi
```

### The Trunk Bookmark Exclusion Sub-section.

The session-bookmark.sh add subcommand explicitly skips the trunk worktree path. The trunk worktree is identified as the repo root. No bookmark is created for it. The teardown orphan check also explicitly excludes the repo root from orphan detection.

```bash
if [ "$wt_path" = "$REPO_ROOT" ]; then
  echo "Skipping trunk — trunk is never bookmarked."
  return 0
fi
```

## The Lifecycle Section.

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-02 | | Initial spec |
