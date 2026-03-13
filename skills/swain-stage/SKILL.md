---
name: swain-stage
description: "Tmux workspace manager — creates layout presets (review, browse, focus), opens editor/browser/shell panes, runs an animated MOTD status panel, and lets the agent directly manage panes during work. Only activates in tmux sessions."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Tmux workspace and pane management
  version: 1.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# Stage

Tmux workspace manager for swain. Creates pane layouts, manages an animated MOTD status panel, and gives the agent direct control over the visual workspace.

**Prerequisite:** Must be running inside a tmux session (`$TMUX` must be set). If not in tmux, inform the user and exit gracefully.

## Script location

Swain project skills live under `skills/` in the project root. For this skill, use:
- `skills/swain-stage/scripts/swain-stage.sh` — main tmux layout and pane manager
- `skills/swain-stage/scripts/swain-motd.py` — MOTD status panel (Textual TUI, runs via `uv run`)
- `skills/swain-stage/scripts/swain-motd.sh` — legacy bash MOTD (kept as fallback if uv/Textual unavailable)
- `skills/swain-stage/references/layouts/` — layout presets
- `skills/swain-stage/references/yazi/` — bundled Yazi config used when `fileBrowser` resolves to `yazi`

## Commands

### Layout presets

Apply a named layout. Available presets are in `skills/swain-stage/references/layouts/`:

| Layout | Description |
|--------|-------------|
| **focus** | Agent pane + MOTD top-right + file browser bottom-right |
| **review** | Agent + editor (changed files) + MOTD |
| **browse** | Agent + file browser + MOTD |

```bash
bash skills/swain-stage/scripts/swain-stage.sh layout review
bash skills/swain-stage/scripts/swain-stage.sh layout browse
bash skills/swain-stage/scripts/swain-stage.sh layout focus
```

The default layout is configured in `swain.settings.json` under `stage.defaultLayout` (default: `focus`).

Users can override layout definitions in `swain.settings.json` under `stage.layouts.<name>`.

### Open individual panes

Open a specific pane type without applying a full layout:

```bash
bash skills/swain-stage/scripts/swain-stage.sh pane editor file1.py file2.py   # editor with specific files
bash skills/swain-stage/scripts/swain-stage.sh pane browser                      # file browser at repo root
bash skills/swain-stage/scripts/swain-stage.sh pane browser /some/path           # file browser at specific path
bash skills/swain-stage/scripts/swain-stage.sh pane motd                         # MOTD status panel
bash skills/swain-stage/scripts/swain-stage.sh pane shell                        # plain shell
```

### MOTD management

The MOTD pane shows a dynamic status panel with:
- Project name, branch, and dirty state
- Animated spinner when the agent is working (braille, dots, or bar style)
- Current agent context (what it's doing)
- Active epic with progress ratio (from swain-status cache)
- Active tk task
- Ready (actionable) artifact count
- Last commit info
- Assigned GitHub issue count
- Count of touched files

The MOTD is a Textual TUI app (`swain-motd.py`) launched via `uv run`. It reads project data from `status-cache.json` (written by swain-status) when available, falling back to direct git/tk queries when the cache is absent or stale (>5 min). Agent state (spinner, context) is always read from `stage-status.json` for real-time responsiveness. Textual handles Unicode width correctly, provides proper box drawing with rounded corners, and supports color theming.

**Reactive status via hooks:** `stage-status-hook.sh` is configured as a Claude Code hook (PostToolUse, Stop, SubagentStart, SubagentStop) in `.claude/settings.json`. It writes `stage-status.json` automatically so the MOTD spinner reflects real agent activity without manual `motd update` calls.

Control the MOTD:

```bash
bash skills/swain-stage/scripts/swain-stage.sh motd start                        # start MOTD in a new pane
bash skills/swain-stage/scripts/swain-stage.sh motd stop                         # kill the MOTD pane
bash skills/swain-stage/scripts/swain-stage.sh motd update "reviewing auth module"  # update context
bash skills/swain-stage/scripts/swain-stage.sh motd update "idle"                # mark as idle
bash skills/swain-stage/scripts/swain-stage.sh motd update "done"                # mark as done/idle
```

### Close panes

```bash
bash skills/swain-stage/scripts/swain-stage.sh close right     # close the right pane
bash skills/swain-stage/scripts/swain-stage.sh close bottom    # close the bottom pane
bash skills/swain-stage/scripts/swain-stage.sh close all       # reset to single pane
```

### Status

```bash
bash skills/swain-stage/scripts/swain-stage.sh status          # show current layout info
```

### Reset

```bash
bash skills/swain-stage/scripts/swain-stage.sh reset           # kill all panes except current
```

## Agent-triggered pane operations

The agent should use swain-stage directly during work. Recommended patterns:

### After making changes — open review

When you've finished modifying files, open them for the user to review:

```bash
bash skills/swain-stage/scripts/swain-stage.sh motd update "changes ready for review"
bash skills/swain-stage/scripts/swain-stage.sh pane editor file1.py file2.py
```

### During research — open file browser

When exploring the codebase:

```bash
bash skills/swain-stage/scripts/swain-stage.sh pane browser src/components/
```

### Update context as you work

Keep the MOTD informed of what you're doing:

```bash
bash skills/swain-stage/scripts/swain-stage.sh motd update "analyzing test failures"
bash skills/swain-stage/scripts/swain-stage.sh motd update "writing migration script"
bash skills/swain-stage/scripts/swain-stage.sh motd update "done"
```

### Clean up when done

```bash
bash skills/swain-stage/scripts/swain-stage.sh close right
bash skills/swain-stage/scripts/swain-stage.sh motd update "idle"
```

## Settings

Read from `swain.settings.json` (project) and `~/.config/swain/settings.json` (user override). User settings take precedence.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `editor` | string | `auto` | Editor command. `auto` detects: micro > helix > nano > vim |
| `fileBrowser` | string | `auto` | File browser command. `auto` detects: yazi > nnn > ranger > mc |
| `stage.defaultLayout` | string | `focus` | Layout applied by default |
| `stage.motd.refreshInterval` | number | `5` | MOTD refresh interval in seconds (idle) |
| `stage.motd.spinnerStyle` | string | `braille` | Spinner animation: `braille`, `dots`, or `bar` |
| `stage.layouts` | object | `{}` | User-defined layout overrides (same schema as preset files) |

## Error handling

- If not in tmux: report clearly and exit. Do not attempt tmux commands.
- If editor/file browser is not installed: warn the user and suggest alternatives or `swain.settings.json` override.
- If the file browser resolves to `yazi`, swain-stage injects the bundled config in `skills/swain-stage/references/yazi/` so text files open with the system default app and directory colors remain readable on dark terminals.
- If jq is not available: warn that settings cannot be read, use hardcoded defaults.
- Pane operations are best-effort — if a pane can't be created or found, warn but don't fail the session.
