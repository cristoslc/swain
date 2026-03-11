---
name: swain-session
description: "Session management — restores terminal tab name, user preferences, and context bookmarks on session start. Auto-invoked at session start via AGENTS.md. Also invokable manually to change preferences or bookmark context for the next session."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Session state and identity management
  version: 1.1.0
  author: cristos
  source: swain
---

# Session

Manages session identity, preferences, and context continuity across agent sessions. This skill is agent-agnostic — it relies on AGENTS.md for auto-invocation.

## Auto-run behavior

This skill is invoked automatically at session start (see AGENTS.md). When auto-invoked:

1. **Restore tab name** — run the tab-naming script
2. **Load preferences** — read session.json and apply any stored preferences
3. **Show context bookmark** — if a previous session left a context note, display it

When invoked manually, the user can change preferences or bookmark context.

## Step 1 — Set terminal tab name (tmux only)

Check if `$TMUX` is set. If yes, run the tab-naming script:

```bash
bash "$(dirname "$0")/../skills/swain-session/scripts/swain-tab-name.sh" --auto
```

Use the project root to locate the script. The script reads `swain.settings.json` for the tab name format (default: `{project} @ {branch}`).

If this fails (e.g., not in a git repo), set a fallback title of "swain".

**If `$TMUX` is NOT set**, skip tab naming and show this tip:

> **Tip:** Tab naming and workspace layouts require tmux. Run `tmux` before starting Claude Code to enable `/swain-session` tab naming and `/swain-stage` layouts.

## Step 2 — Load session preferences

Read the session state file. The file location is:

```
~/.claude/projects/<project-path-slug>/memory/session.json
```

Where `<project-path-slug>` is the Claude Code memory directory for the current project.

The session.json schema:

```json
{
  "lastBranch": "main",
  "lastContext": "Working on swain-session skill",
  "preferences": {
    "verbosity": "concise"
  },
  "bookmark": {
    "note": "Left off implementing the MOTD animation",
    "files": ["skills/swain-stage/scripts/swain-motd.sh"],
    "timestamp": "2026-03-10T14:32:00Z"
  }
}
```

If the file exists:
- Read and apply preferences (currently informational — future skills can check these)
- If `bookmark` exists and has a `note`, display it to the user:
  > **Resuming session** — Last time: {note}
  > Files: {files list, if any}
- Update `lastBranch` to the current branch

If the file does not exist, create it with defaults.

## Step 3 — Suggest swain-stage (tmux only)

If `$TMUX` is set and swain-stage is available, inform the user:

> Run `/swain-stage` to set up your workspace layout.

Do not auto-invoke swain-stage — let the user decide.

## Manual invocation commands

When invoked explicitly by the user, support these operations:

### Set tab name
User says something like "set tab name to X" or "rename tab":
```bash
bash scripts/swain-tab-name.sh "Custom Name"
```

### Bookmark context
User says "remember where I am" or "bookmark this":
- Ask what they're working on (or infer from conversation context)
- Write to session.json `bookmark` field with note, relevant files, and timestamp

### Clear bookmark
User says "clear bookmark" or "fresh start":
- Remove the `bookmark` field from session.json

### Show session info
User says "session info" or "what's my session":
- Display current tab name, branch, preferences, bookmark status

### Set preference
User says "set preference X to Y":
- Update `preferences` in session.json

## Post-operation bookmark (auto-update protocol)

Other swain skills update the session bookmark after completing operations. This gives the developer a "where I left off" marker without requiring manual bookmarking.

### When to update

A skill should update the bookmark when it completes a **state-changing operation** — artifact transitions, task updates, commits, releases. Read-only operations (status, discover, help) should NOT update the bookmark.

### How to update

After completing operations, write to session.json's `bookmark` field:

```bash
SESSION_FILE="$(find ~/.claude/projects/ -path '*/memory/session.json' -print -quit 2>/dev/null)"
if [ -n "$SESSION_FILE" ] && command -v jq >/dev/null 2>&1; then
  jq --arg note "$BOOKMARK_NOTE" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '.bookmark = {note: $note, timestamp: $ts}' "$SESSION_FILE" > "$SESSION_FILE.tmp" \
    && mv "$SESSION_FILE.tmp" "$SESSION_FILE"
fi
```

Or equivalently, use the Edit tool to update the JSON directly.

### Bookmark content

The note should be a concise summary of what was done, e.g.:
- "Transitioned SPEC-001 to Approved, created SPEC-002 draft"
- "Completed task 'implement auth middleware', started 'write tests'"
- "Pushed 3 commits to feature/search-skill"
- "Released v1.2.0"

Include `files` array only when specific files are central to the work (not for every operation).

## Settings

This skill reads from `swain.settings.json` (project root) and `~/.config/swain/settings.json` (user override). User settings take precedence.

Relevant settings:
- `terminal.tabNameFormat` — format string for tab names. Supports `{project}` and `{branch}` placeholders. Default: `{project} @ {branch}`

## Error handling

- If jq is not available, warn the user and skip JSON operations. Tab naming still works without jq.
- If git is not available, use the directory name as the project name and skip branch detection.
- Never fail hard — session management is a convenience, not a gate.
