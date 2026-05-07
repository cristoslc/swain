---
source-id: omo-slim-multiplexer
title: oh-my-opencode-slim — Multiplexer Integration Guide
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/docs/multiplexer-integration.md
fetched: 2026-05-05
type: documentation
---

# Multiplexer Integration Guide

Use tmux or Zellij to watch subagents work in live panes while OpenCode runs in your main session.

## Quick Start

1. Enable in config:
```jsonc
{ "multiplexer": { "type": "auto", "layout": "main-vertical", "main_pane_size": 60 } }
```

2. Start OpenCode inside tmux or Zellij:
```bash
# Tmux:
tmux && opencode --port 4096

# Zellij:
zellij && opencode --port 4096
```

3. Trigger delegated work — new panes appear automatically.

Note: Requires `--port` flag matching `OPENCODE_PORT` env var (workaround for opencode#9099).

## Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `multiplexer.type` | string | `"none"` | `"auto"`, `"tmux"`, `"zellij"`, `"none"` |
| `multiplexer.layout` | string | `"main-vertical"` | Layout preset (tmux only) |
| `multiplexer.main_pane_size` | number | `60` | Main pane % (20–80, tmux only) |

## Supported Multiplexers

| Multiplexer | Status | Notes |
|-------------|--------|-------|
| Tmux | Full support | Layout control: main-vertical, main-horizontal, tiled, even-horizontal, even-vertical |
| Zellij | Supported | Dedicated `opencode-agents` tab; reuses default pane |

## Legacy Config

```jsonc
{ "tmux": { "enabled": true, "layout": "main-vertical", "main_pane_size": 60 } }
```
Auto-converts to `multiplexer.type: "tmux"`.

## Layouts (Tmux Only)

| Layout | Description |
|--------|-------------|
| `main-vertical` | Main session left, agents stacked right |
| `main-horizontal` | Main session top, agents below |
| `tiled` | Equal-sized grid |
| `even-horizontal` | All side by side |
| `even-vertical` | All stacked vertically |

## Multiple Sessions

Use random high ports per session:
```bash
omos() {
  local port=$(jot -r 1 49152 65535)
  OPENCODE_PORT="$port" opencode --port "$port" "$@"
}
```
