---
title: Troubleshooting
url: https://www.getagentcraft.com/docs/troubleshooting
fetched: 2026-05-04
type: documentation
---

# Troubleshooting

Diagnostics, common issues, and recovery.

## Diagnostics

Run the built-in diagnostic tool:

```
npx @idosal/agentcraft doctor
```

This checks:

- Whether Claude Code is installed
- Whether the CLI is in your PATH
- Whether hooks are properly installed
- Whether the server is running
- Node.js version compatibility

## Common Issues

### Hooks not installed / heroes not appearing

```
npx @idosal/agentcraft install --force
```

This reinstalls hooks. If external Claude Code sessions still don't appear, verify hooks are present:

```
npx @idosal/agentcraft doctor
```

### Port 2468 already in use

```
npx @idosal/agentcraft stop
# Or use a different port:
npx @idosal/agentcraft start --port 3002
```

### Internal heroes spawn but never become active

Check that Claude Code is authenticated and working in your terminal:

```
claude --version
```

Internal heroes use the same Claude Code binary.

### Agent Teams members not visible

Ensure tmux is installed for full teammate visibility. Without tmux, teammates run in-process and have limited status tracking. Also verify team configs exist at ~/.claude/teams/.

### OpenCode heroes not spawning

Verify OpenCode is installed and in your PATH. AgentCraft detects the binary at startup — if you installed OpenCode after starting the server, restart the server.

### Cursor option grayed out

The Cursor CLI must be detected at startup. Verify Cursor is installed and the cursor command is available in your terminal.

## Restore Settings

If hook installation caused issues with your Claude Code settings:

```
npx @idosal/agentcraft restore
```

This restores ~/.claude/settings.json from the backup taken before installation.

## Getting Help

- Discord — Get help and share feedback: https://discord.gg/nEaZAH7C7F
- Twitter / X — Follow for updates: https://x.com/idosal1