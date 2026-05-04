---
title: Cursor Integration
url: https://www.getagentcraft.com/docs/integrations/cursor
fetched: 2026-05-04
type: documentation
---

# Cursor

Integration with Cursor's agent mode via CLI.

AgentCraft supports Cursor as a third AI coding agent alongside Claude Code and OpenCode.

## Setup

If Cursor is installed (~/.cursor/ directory or cursor CLI on PATH), AgentCraft automatically installs hooks to ~/.cursor/hooks.json during setup. These hooks report session events (spawn, active, idle, file operations) to AgentCraft in real time.

To install or update Cursor hooks manually:

```
npx @idosal/agentcraft install
```

To remove Cursor hooks:

```
npx @idosal/agentcraft uninstall
```

## Spawning Cursor Heroes

Press E at the Town Hall (or in the command grid) to spawn a Cursor hero. The E option is grayed out if the Cursor CLI is not detected.

## Model Selection

When you select a Cursor hero, the model dropdown shows a flat list of Cursor-specific model identifiers:

- auto
- sonnet-4
- sonnet-4-thinking
- opus-4.1
- gpt-5
- gemini-3-pro
- grok

AgentCraft auto-discovers available models by parsing cursor agent --help output at startup. If the Cursor CLI is not reachable, a built-in fallback list is used.

Cursor model identifiers are short names — they differ from Claude Code and OpenCode model strings.

## Features

Cursor heroes appear on the map and support core AgentCraft features including:

- Real-time status tracking
- Mission tracking
- Map visualization
- Hero selection and control groups

## Notes

- Cursor integration uses Cursor's own model configuration and subscription
- Some advanced features (plan approval, permission handling, Agent Teams) are Claude Code-specific