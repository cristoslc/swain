---
title: CLI Reference
url: https://www.getagentcraft.com/docs/cli
fetched: 2026-05-04
type: documentation
---

# CLI Reference

Command reference for the AgentCraft CLI.

## Commands

| Command | Description |
| --- | --- |
| npx @idosal/agentcraft | Guided setup: detect CLIs, install hooks, start server, open browser |
| agentcraft start | Start server. Installs hooks if missing. Options: -p/--port, --no-browser, -d/--daemon, --all-projects |
| agentcraft stop | Stop a running server (SIGTERM, then SIGKILL after 5s) |
| agentcraft status | Show server PID, port, and uptime |
| agentcraft open | Open the UI in a browser (server must be running) |
| agentcraft install | Install hooks only (no server). --force to reinstall |
| agentcraft uninstall | Remove AgentCraft hooks, preserving user hooks |
| agentcraft restore | Restore ~/.claude/settings.json from pre-install backup |
| agentcraft logout | Clear auth tokens from ~/.agentcraft/auth.json |
| agentcraft doctor | Run diagnostics |

## Default Flow

Running npx @idosal/agentcraft with no arguments performs the guided setup:

1. Checks ~/.claude/ exists (Claude Code installed)
2. Backs up settings.json to settings.backup.json
3. Installs event hooks into ~/.claude/settings.json (merges without touching existing hooks)
4. If OpenCode is detected, installs the plugin to ~/.config/opencode/plugins/agentcraft.js
5. If Cursor is detected, installs hooks to ~/.cursor/hooks.json
6. Starts the server on port 2468
7. Opens the browser UI

## Server Modes

### Foreground (default)

```
npx @idosal/agentcraft
```

The server runs in the foreground. Press Ctrl+C to stop.

### Daemon

```
npx @idosal/agentcraft start --daemon   # or: start -d
npx @idosal/agentcraft stop             # Stop the daemon later
```

### Custom Port

```
npx @idosal/agentcraft start --port 3002   # or: start -p 3002
```

### All Projects

By default, only agents from the current working directory are shown. To display sessions from all projects:

```
npx @idosal/agentcraft start --all-projects
```

## Diagnostics

```
npx @idosal/agentcraft doctor
```

Checks:

- Whether Claude Code is installed
- Whether the CLI is in your PATH
- Whether hooks are properly installed in settings
- Whether the server is running
- Node.js version compatibility

## Hook Management

### Install / Reinstall

```
npx @idosal/agentcraft install --force
```

Hooks are identified by the PLUGIN_DIR path in their command strings. AgentCraft hooks are merged with your existing hooks — user-defined hooks are never touched.

### Uninstall

```
npx @idosal/agentcraft uninstall
```

Removes only AgentCraft hooks, preserving any user-defined hooks.

### Restore

```
npx @idosal/agentcraft restore
```

Restores ~/.claude/settings.json from the backup taken before the last install. Only the most recent pre-install state is preserved.

## Configuration Files

All AgentCraft config lives in ~/.agentcraft/:

| File | Purpose |
| --- | --- |
| config.json | Port, autoOpenBrowser, API keys |
| auth.json | Auth tokens (0o600 permissions) |
| server.pid | PID of daemon-mode server |
| mission-history.json | Persisted completed missions |