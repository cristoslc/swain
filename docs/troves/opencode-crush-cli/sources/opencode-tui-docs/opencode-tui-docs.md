---
source-id: "opencode-tui-docs"
title: "TUI | OpenCode — Terminal user interface documentation"
type: web
url: "https://opencode.ai/docs/tui/"
fetched: 2026-04-07T01:57:49Z
hash: "27b6f876038a9e82aca8dc3b2d3d0ea6b659f5546bbe43e3447a23476e348a9d"
---

# TUI | OpenCode

OpenCode provides an interactive terminal interface or TUI for working on your projects with an LLM.

Running OpenCode starts the TUI for the current directory:

```
opencode
```

Or for a specific working directory:

```
opencode /path/to/project
```

## File references

Reference files in messages using `@`. This does a fuzzy file search in the current working directory:

```
How is auth handled in @packages/functions/src/api/index.ts?
```

The file content is added to the conversation automatically.

## Bash commands

Start a message with `!` to run a shell command:

```
!ls -la
```

The output is added to the conversation as a tool result.

## Slash commands

Type `/` followed by a command name to execute actions. Most commands also have a keybind using `ctrl+x` as the default leader key.

| Command | Aliases | Keybind | Description |
| --- | --- | --- | --- |
| `/connect` | | | Add a provider and API key |
| `/compact` | `/summarize` | `ctrl+x c` | Compact the current session |
| `/details` | | `ctrl+x d` | Toggle tool execution details |
| `/editor` | | `ctrl+x e` | Open external editor for composing messages |
| `/exit` | `/quit`, `/q` | `ctrl+x q` | Exit OpenCode |
| `/export` | | `ctrl+x x` | Export conversation to Markdown and open in editor |
| `/help` | | `ctrl+x h` | Show the help dialog |
| `/init` | | `ctrl+x i` | Guided setup for creating or updating `AGENTS.md` |
| `/models` | | `ctrl+x m` | List available models |
| `/new` | `/clear` | `ctrl+x n` | Start a new session |
| `/redo` | | `ctrl+x r` | Redo a previously undone message (requires git repo) |
| `/sessions` | `/resume`, `/continue` | `ctrl+x l` | List and switch between sessions |
| `/share` | | `ctrl+x s` | Share current session |
| `/themes` | | `ctrl+x t` | List available themes |
| `/thinking` | | | Toggle visibility of thinking/reasoning blocks |
| `/undo` | | `ctrl+x u` | Undo last message and revert file changes (requires git repo) |
| `/unshare` | | | Unshare current session |

Note: `/undo` and `/redo` use Git to manage file changes — the project must be a git repository.

## Editor setup

Both `/editor` and `/export` use the editor in the `EDITOR` environment variable:

```bash
export EDITOR=vim
# For GUI editors, include --wait:
export EDITOR="code --wait"
```

## Configuration

Customize TUI behavior through `tui.json` (or `tui.jsonc`). This is **separate** from `opencode.json`, which configures server/runtime behavior.

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "opencode",
  "keybinds": {
    "leader": "ctrl+x"
  },
  "scroll_speed": 3,
  "scroll_acceleration": {
    "enabled": true
  },
  "diff_style": "auto",
  "mouse": true
}
```

### Options

- `theme` — UI theme.
- `keybinds` — Keyboard shortcut customization.
- `scroll_acceleration.enabled` — macOS-style scroll acceleration. Takes precedence over `scroll_speed`.
- `scroll_speed` — Scroll speed (minimum: `0.001`, default: `3`). Ignored if `scroll_acceleration.enabled` is true.
- `diff_style` — Diff rendering: `"auto"` adapts to terminal width, `"stacked"` always single-column.
- `mouse` — Enable/disable mouse capture (default: `true`).

Use `OPENCODE_TUI_CONFIG` to load a custom TUI config path.
