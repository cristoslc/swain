---
title: Installation & Setup
url: https://www.getagentcraft.com/docs/getting-started
fetched: 2026-05-04
type: documentation
---

# Installation & Setup

Install AgentCraft and launch it for the first time.

## Prerequisites

- **Node.js** 18 or later
- At least one supported AI agent CLI installed:
  - Claude Code (npm install -g @anthropic-ai/claude-code)
  - OpenCode (curl -fsSL https://opencode.ai/install | sh)
  - Cursor

## Install

Run the guided setup:

```
npx @idosal/agentcraft
```

This will:

1. Auto-detect any installed agent CLIs (Claude Code, OpenCode, Cursor)
2. Install hooks for each detected agent (merges without touching your existing hooks)
3. Start the server on port 2468
4. Open the browser UI automatically

For each detected agent:

- Claude Code — hooks installed to ~/.claude/settings.json (backed up to settings.backup.json)
- OpenCode — plugin installed to ~/.config/opencode/plugins/agentcraft.js
- Cursor — hooks installed to ~/.cursor/hooks.json

### Force Reinstall

```
npx @idosal/agentcraft install --force
```

### Run in Background (Daemon Mode)

```
npx @idosal/agentcraft start -d
npx @idosal/agentcraft stop # Stop later
```

### Custom Port

```
npx @idosal/agentcraft start --port 3002
# or shorthand:
npx @idosal/agentcraft start -p 3002
```

### Show All Projects

By default AgentCraft only shows agents from the current directory. To see sessions from all projects:

```
npx @idosal/agentcraft start --all-projects
```

## First Launch

On first launch, an interactive tutorial guides you through the basics:

1. Welcome — Introduction to the RTS interface
2. Commands — The command grid at the bottom; spawn your first hero
3. Hero Spawn — Send your first prompt to the hero
4. Observe — Activity bubbles and the yellow glow indicating the agent needs input
5. Status Widget — The agent status panel showing all heroes
6. Complete — The War Advisor introduces itself for ongoing tips

Steps 2 and 3 wait for you to take action before advancing.

## Spawning Heroes

Use the Town Hall command grid:

| Key | Action |
| --- | --- |
| Q | Spawn a Claude Code agent |
| W | Spawn an OpenCode agent |
| E | Spawn a Cursor agent |
| R | Open worktree picker |
| A | View active sessions |
| F | Toggle integrated terminal |

External sessions (agents started in a separate terminal) are automatically detected and appear on the map.

## Verify Installation

Run diagnostics:

```
npx @idosal/agentcraft doctor
```

This checks: CLI installed, hooks in PATH, hooks present in settings, server running, Node.js version.

## Next Steps

- Explore keyboard shortcuts
- Configure settings
- Learn about features