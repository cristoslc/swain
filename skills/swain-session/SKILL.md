---
name: swain-session
description: "Session management and project status dashboard. Owns the full session lifecycle (start/work/close/resume), focus lane, bookmarks, worktree auto-isolation, and tab naming. Also serves as the project status dashboard — shows active epics, progress, actionable next steps, blocked items, tasks, GitHub issues, and recommendations. Triggers on: 'session', 'status', 'what's next', 'dashboard', 'overview', 'where are we', 'what should I work on', 'show me priorities', 'bookmark', 'focus on', 'session info'."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, EnterWorktree, ExitWorktree
metadata:
  short-description: Session state and identity management
  version: 1.3.0
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

## Session purpose text

When the operator launches with free text (e.g., `swain new bug about timestamps`), the launcher passes it as part of the initial prompt: `/swain-session Session purpose: new bug about timestamps`.

When session purpose text is present in the invocation:
1. Write it immediately as the session bookmark note (using swain-bookmark.sh)
2. Display it: `**Session purpose:** <text>`

Detection: if the skill is invoked with text after `/swain-session` (e.g., `/swain-session Session purpose: ...`), extract everything after "Session purpose: " as the purpose text.

For runtimes that don't support initial prompts (e.g., crush), check the `SWAIN_PURPOSE` environment variable as a fallback.

## Steps 1–2 — Bootstrap (tab naming + worktree detection + session load)

Run the consolidated bootstrap script in a single call:

```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-bootstrap.sh' -print -quit 2>/dev/null)" --auto
```

The script handles tab naming (tmux only), worktree isolation detection, and session.json loading atomically. It emits structured JSON:

```json
{
  "tab": "project @ branch",
  "worktree": { "isolated": false, "path": null, "branch": "trunk" },
  "session": {
    "focus": "VISION-001",
    "bookmark": "Left off implementing the bootstrap script",
    "lastBranch": "trunk"
  },
  "warnings": []
}
```

**After receiving the JSON output:**

1. If `worktree.isolated` is `false`: use the `EnterWorktree` tool to create an isolated worktree. Generate the worktree name by running:
   ```bash
   bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-worktree-name.sh' -print -quit 2>/dev/null)"
   ```
   Pass the script's stdout as the `name` parameter to `EnterWorktree`. For descriptive names, pass context as an argument: `... swain-worktree-name.sh' ...) "spec-174"`. Never use a static name like "session" (SPEC-174). If `EnterWorktree` fails with a branch-exists error, re-run the script (it generates a fresh suffix each time) and retry once. Then re-run the bootstrap with the new path:
   ```bash
   bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-bootstrap.sh' -print -quit 2>/dev/null)" --path "$(pwd)" --skip-worktree --auto
   ```
   If `EnterWorktree` fails or is unavailable, log a warning and proceed — swain-do will attempt isolation at dispatch time as a fallback.

2. If `session.bookmark` is not null, display it:
   > **Resuming session** — Last time: {bookmark}

3. If `session.focus` is not null, display the focus lane.

4. Display any `warnings` entries.

**If `$TMUX` is NOT set** (detected by absence of `tab` in the JSON), check whether tmux is installed:
- **tmux not installed:** Offer to install it (`brew install tmux`).
- **tmux installed but not in a session:** Show: `[note] Not in a tmux session — session tab and pane features unavailable`

The operator can say "exit worktree" or "back to main" at any time — call `ExitWorktree` to leave isolation.

### Worktree / branch changes (agent-agnostic)

When an agent enters a worktree or switches branches, re-run the bootstrap with `--path` to update the tab name:

```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-bootstrap.sh' -print -quit 2>/dev/null)" --path "$NEW_WORKDIR" --skip-worktree --auto
```

This is agent-agnostic — works in Claude Code, opencode, gemini cli, codex, copilot, or any agent that reads AGENTS.md and can run bash commands.

### Session.json schema

```json
{
  "lastBranch": "trunk",
  "lastContext": "Working on swain-session skill",
  "preferences": {
    "verbosity": "concise"
  },
  "bookmark": {
    "note": "Left off implementing the bootstrap script",
    "files": ["skills/swain-session/SKILL.md"],
    "timestamp": "2026-03-10T14:32:00Z"
  }
}
```

**Migration:** If `.agents/session.json` does not exist but the old global location (`~/.claude/projects/<project-path-slug>/memory/session.json`) does, the bootstrap script copies it automatically.

## Session Lifecycle (SPEC-119)

swain-session owns a bounded session lifecycle: **start → work → close → resume**. Session state is tracked in `.agents/session-state.json` via the `swain-session-state.sh` script.

### Session start

After bootstrap completes and the worktree is ready, initialize the session lifecycle:

```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-state.sh' -print -quit 2>/dev/null)" init --focus "<FOCUS-ID>" --session-roadmap "$(pwd)/SESSION-ROADMAP.md" --repo-root "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
```

This:
1. Creates `.agents/session-state.json` with focus lane, decision budget (default 5), and start time
2. Generates `SESSION-ROADMAP.md` via `chart.sh session --focus <ID>`

The focus lane defaults to the previous session's lane (from bootstrap JSON `session.focus`). Confirm with the operator or accept their redirect.

Custom decision budget: `--budget 7`

### During work — recording decisions

When the operator or agent makes a decision (approves a spec, chooses an approach, sets direction), record it:

```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-state.sh' -print -quit 2>/dev/null)" record-decision --note "Approved SPEC-119 implementation approach"
```

### Session close

When the operator says "done", "wrap up", "close session", or the decision budget is reached:

```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-state.sh' -print -quit 2>/dev/null)" close --walkaway "Completed SPEC-119 tests and state management" --session-roadmap "$(pwd)/SESSION-ROADMAP.md"
```

This:
1. Sets session phase to `closed` with end time
2. Appends the walk-away signal to SESSION-ROADMAP.md
3. The agent should then commit SESSION-ROADMAP.md to git

### Session resume

On the next session start, after bootstrap, check for a previous session:

```bash
bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-session/scripts/swain-session-state.sh' -print -quit 2>/dev/null)" resume
```

This outputs the previous session's focus lane, walkaway note, and decision count. Display it to the operator so they can decide whether to continue or start fresh.

### Session state schema

```json
{
  "session_id": "session-20260328-220634-4ad1",
  "focus_lane": "INITIATIVE-019",
  "phase": "active",
  "start_time": "2026-03-28T22:06:34Z",
  "end_time": null,
  "decision_budget": 5,
  "decisions_made": 0,
  "decisions": [],
  "walkaway": null
}
```

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

Focus lane is stored in `.agents/session.json` under the `focus_lane` key. It persists across status checks within a session. The status dashboard reads it to filter recommendations and show peripheral awareness for non-focus visions.

## Status Dashboard (absorbed from swain-status — SPEC-122)

swain-session now owns the project status dashboard. When the operator says "status", "what's next", "dashboard", "overview", "where are we", "what should I work on", or "show me priorities", run the status script:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STATUS_SCRIPT="$(find "$REPO_ROOT" -path '*/swain-session/scripts/swain-status.sh' -print -quit 2>/dev/null)"
[ -n "$STATUS_SCRIPT" ] && bash "$STATUS_SCRIPT" --refresh || echo "swain-status.sh not found"
```

For compact mode (MOTD): `bash "$STATUS_SCRIPT" --compact`

After the script runs, present a structured agent summary following [references/agent-summary-template.md](references/agent-summary-template.md).

### Cache

Status writes to `.agents/status-cache.json` with 120-second TTL. Use `--refresh` to bypass, `--json` for raw output.

### Recommendation

Read `.priority.recommendations[0]` from the JSON cache. When a focus lane is set, recommendations scope to that vision/initiative.

### Mode Inference

1. Both specs in review AND strategic decisions pending → ask operator
2. Specs awaiting review → detail mode
3. Focus lane + pending decisions → vision mode
4. Nothing actionable → vision mode (master plan mirror)

### Decisions Needed (roadmap integration)

Uses `chart.sh roadmap --json` for Eisenhower classification. Show top 5 items from "Do First" and "Schedule" quadrants that need operator decisions.

## Settings

This skill reads from `swain.settings.json` (project root) and `~/.config/swain/settings.json` (user override). User settings take precedence.

Relevant settings:
- `terminal.tabNameFormat` — format string for tab names. Supports `{project}` and `{branch}` placeholders. Default: `{project} @ {branch}`

## Error handling

- If jq is not available, warn the user and skip JSON operations. Tab naming still works without jq.
- If git is not available, use the directory name as the project name and skip branch detection.
- Never fail hard — session management is a convenience, not a gate.
