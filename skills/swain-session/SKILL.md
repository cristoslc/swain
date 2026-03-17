---
name: swain-session
description: "Session management — restores terminal tab name, user preferences, and context bookmarks on session start. Auto-invoked at session start via AGENTS.md. Also invokable manually to change preferences or bookmark context for the next session."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Session state and identity management
  version: 1.2.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# Session

Manages session identity, preferences, and context continuity across agent sessions. This skill is agent-agnostic — it relies on AGENTS.md for auto-invocation.

## Auto-run behavior

This skill is invoked automatically at session start (see AGENTS.md). When auto-invoked:

1. **Restore tab name** — run the tab-naming script
2. **Load preferences** — read session.json and apply any stored preferences
3. **Show context bookmark** — if a previous session left a context note, display it

When invoked manually, the user can change preferences or bookmark context.

## Step 1 — Set terminal tab/session name (tmux only)

Check if `$TMUX` is set. If yes, run the tab-naming script:

```bash
bash skills/swain-session/scripts/swain-tab-name.sh --auto
```

Use the project root to locate the script. The script reads `swain.settings.json` for the tab name format (default: `{project} @ {branch}`).

The script renames **both** the tmux window (tab) and the tmux session. It also installs a `pane-focus-in` hook so names update automatically when the operator switches between tmux panes in different git repos/branches.

If this fails (e.g., not in a git repo), set a fallback title of "swain".

### Worktree / branch changes (agent-agnostic)

When an agent enters a worktree or switches branches, the tmux pane's tracked CWD does not update (agent commands run in subshells). **Any agent** that changes its working context MUST re-run the tab-naming script with `--path`:

```bash
bash skills/swain-session/scripts/swain-tab-name.sh --path "$NEW_WORKDIR" --auto
```

This is agent-agnostic — it works in Claude Code, opencode, gemini cli, codex, copilot, or any other agent that reads AGENTS.md and can run bash commands. The `--path` flag takes priority over the pane's CWD.

**If `$TMUX` is NOT set**, skip tab naming and show this tip:

> **Tip:** Tab naming and workspace layouts require tmux. Run `tmux` before starting Claude Code to enable `/swain-session` tab naming and `/swain-stage` layouts.

## Step 2 — Load session preferences

Read the session state file. The file location is:

```
<project-root>/.agents/session.json
```

This keeps session state per-project, version-controlled, and visible to collaborators.

**Migration:** If `.agents/session.json` does not exist but the old global location (`~/.claude/projects/<project-path-slug>/memory/session.json`) does, copy it to `.agents/session.json` on first access.

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
bash skills/swain-session/scripts/swain-tab-name.sh "Custom Name"
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
- If the bookmark note contains an artifact ID (e.g., `SPEC-052`, `EPIC-018`), show the Vision ancestry breadcrumb for strategic context. Run `bash skills/swain-design/scripts/chart.sh scope <ID> 2>/dev/null | head -5` to get the parent chain. Display as: `Context: Swain > Operator Situational Awareness > Vision-Rooted Chart Hierarchy`

### Set preference
User says "set preference X to Y":
- Update `preferences` in session.json

## Post-operation bookmark (auto-update protocol)

Other swain skills update the session bookmark after completing operations. This gives the developer a "where I left off" marker without requiring manual bookmarking.

### When to update

A skill should update the bookmark when it completes a **state-changing operation** — artifact transitions, task updates, commits, releases, or status checks.

### How to update

Use `skills/swain-session/scripts/swain-bookmark.sh`:

```bash
# Find the script
BOOKMARK_SCRIPT="$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)"

# Basic note
bash "$BOOKMARK_SCRIPT" "Transitioned SPEC-001 to Approved"

# Note with files
bash "$BOOKMARK_SCRIPT" "Implemented auth middleware" --files src/auth.ts src/auth.test.ts

# Clear bookmark
bash "$BOOKMARK_SCRIPT" --clear
```

The script handles session.json discovery, atomic writes, and graceful degradation (no jq = silent no-op).

## Focus Lane

The operator can set a focus lane to tell swain-status to recommend within a single vision or initiative. This is a steering mechanism — it doesn't hide other work, but frames recommendations around the operator's current focus.

**Setting focus:**
When the operator says "focus on security" or "I'm working on VISION-001", resolve the name to an artifact ID and invoke the focus script.

**Name-to-ID resolution:** If the operator uses a name instead of an ID (e.g., "security" instead of "VISION-001"), search Vision and Initiative artifact titles for the best match using swain chart:
```bash
bash skills/swain-design/scripts/chart.sh --ids --flat 2>/dev/null | grep -i "<name>"
```
If exactly one match, use it. If multiple matches, ask the operator to clarify. If no match, tell the operator no Vision or Initiative matches that name and offer to create one.

```bash
bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-focus.sh' -print -quit 2>/dev/null)" set <RESOLVED-ID>
```

**Clearing focus:**
```bash
bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-focus.sh' -print -quit 2>/dev/null)" clear
```

**Checking focus:**
```bash
bash "$(find . .claude .agents -path '*/swain-session/scripts/swain-focus.sh' -print -quit 2>/dev/null)"
```

Focus lane is stored in `.agents/session.json` under the `focus_lane` key. It persists across status checks within a session. swain-status reads it to filter recommendations and show peripheral awareness for non-focus visions.

## Settings

This skill reads from `swain.settings.json` (project root) and `~/.config/swain/settings.json` (user override). User settings take precedence.

Relevant settings:
- `terminal.tabNameFormat` — format string for tab names. Supports `{project}` and `{branch}` placeholders. Default: `{project} @ {branch}`

## Error handling

- If jq is not available, warn the user and skip JSON operations. Tab naming still works without jq.
- If git is not available, use the directory name as the project name and skip branch detection.
- Never fail hard — session management is a convenience, not a gate.
