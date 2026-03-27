---
name: swain-session
description: "Session management — restores terminal tab name, user preferences, and context bookmarks on session start. Auto-invoked at session start via AGENTS.md. Also invokable manually to set focus, bookmark context, remember where I am, check session info, rename the tmux tab, or update session state for the next session. Manages worktree auto-isolation and focus lane persistence."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, EnterWorktree, ExitWorktree
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
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$(find "$REPO_ROOT" -path '*/swain-session/scripts/swain-tab-name.sh' -print -quit 2>/dev/null)" --auto
```

Use the project root to locate the script. The script reads `swain.settings.json` for the tab name format (default: `{project} @ {branch}`).

The script renames **both** the tmux window (tab) and the tmux session. It also installs a `pane-focus-in` hook so names update automatically when the operator switches between tmux panes in different git repos/branches.

If this fails (e.g., not in a git repo), set a fallback title of "swain".

### Worktree / branch changes (agent-agnostic)

When an agent enters a worktree or switches branches, the tmux pane's tracked CWD does not update (agent commands run in subshells). **Any agent** that changes its working context MUST re-run the tab-naming script with `--path`:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$(find "$REPO_ROOT" -path '*/swain-session/scripts/swain-tab-name.sh' -print -quit 2>/dev/null)" --path "$NEW_WORKDIR" --auto
```

This is agent-agnostic — it works in Claude Code, opencode, gemini cli, codex, copilot, or any other agent that reads AGENTS.md and can run bash commands. The `--path` flag takes priority over the pane's CWD.

**If `$TMUX` is NOT set**, skip tab naming and check whether tmux is installed:

```bash
which tmux
```

- **tmux not installed:** Offer to install it:
  > tmux is not installed. Install it now? I can run `brew install tmux` for you.

  If the user accepts, run `brew install tmux`. Session tab naming will be available on the next session start inside tmux.

- **tmux installed but not in a session:** Show this note:
  > [note] Not in a tmux session — session tab and pane features unavailable

## Step 1.5 — Worktree auto-isolation

After tab naming, detect whether the agent is in the main worktree:

```bash
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null)
[ "$GIT_COMMON" != "$GIT_DIR" ] && IN_WORKTREE=yes || IN_WORKTREE=no
```

**If `IN_WORKTREE=yes`:** Already isolated. Skip to Step 2.

**If `IN_WORKTREE=no`:** Use the `EnterWorktree` tool to create an isolated worktree. **Always pass a unique name** to avoid branch collisions when multiple sessions start concurrently. Generate the name as `session-YYYYMMDD-HHmmss` (e.g., `session-20260327-143022`). If the operator provided a task context (e.g., "working on SPEC-174"), prefer a descriptive name like `spec-174-<slug>` — but always include a disambiguator if the name could collide.

```bash
# Generate a timestamped session name
WORKTREE_NAME="session-$(date +%Y%m%d-%H%M%S)"
```

This is the only mechanism that actually changes the agent's working directory — manual `git worktree add` + `cd` does not persist across tool calls.

After entering the worktree, re-run tab naming to reflect the new branch:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$(find "$REPO_ROOT" -path '*/swain-session/scripts/swain-tab-name.sh' -print -quit 2>/dev/null)" --path "$(pwd)" --auto
```

**If `EnterWorktree` fails or is unavailable:** Log a warning and proceed without isolation. swain-do will attempt isolation at dispatch time as a fallback.

The operator can say "exit worktree" or "back to main" at any time — call `ExitWorktree` to leave isolation.

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
  "lastBranch": "trunk",
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
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$(find "$REPO_ROOT" -path '*/swain-session/scripts/swain-tab-name.sh' -print -quit 2>/dev/null)" "Custom Name"
```

### Bookmark context
User says "remember where I am" or "bookmark this":
- Infer what they're working on from conversation context, or use the note they provided — do not prompt the user
- Write to session.json `bookmark` field with note, relevant files, and timestamp
- If a bookmark already exists, **overwrite it silently without asking for confirmation** — `swain-bookmark.sh` handles atomic writes

### Clear bookmark
User says "clear bookmark" or "fresh start":
- Remove the `bookmark` field from session.json

### Show session info
User says "session info" or "what's my session":
- Display current tab name, branch, preferences, bookmark status
- If the bookmark note contains an artifact ID (e.g., `SPEC-052`, `EPIC-018`), show the Vision ancestry breadcrumb for strategic context. Run `bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)" scope <ID> 2>/dev/null | head -5` to get the parent chain. Display as: `Context: Swain > Operator Situational Awareness > Vision-Rooted Chart Hierarchy`

### Set preference
User says "set preference X to Y":
- Update `preferences` in session.json

## Post-operation bookmark (auto-update protocol)
Other swain skills update the session bookmark after operations. Read [references/bookmark-protocol.md](references/bookmark-protocol.md) for the protocol, invocation patterns, and examples.

## Focus Lane

The operator can set a focus lane to tell swain-status to recommend within a single vision or initiative. This is a steering mechanism — it doesn't hide other work, but frames recommendations around the operator's current focus.

**Setting focus:**
When the operator says "focus on security" or "I'm working on VISION-001", resolve the name to an artifact ID and invoke the focus script.

**Name-to-ID resolution:** If the operator uses a name instead of an ID (e.g., "security" instead of "VISION-001"), search Vision and Initiative artifact titles for the best match using swain chart:
```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/chart.sh' -print -quit 2>/dev/null)" --ids --flat 2>/dev/null | grep -i "<name>"
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
