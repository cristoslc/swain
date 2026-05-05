---
title: Claude Code Integration
url: https://www.getagentcraft.com/docs/integrations/claude-code
fetched: 2026-05-04
type: documentation
---

# Claude Code

Primary integration with Anthropic's Claude Code CLI.

Claude Code is AgentCraft's primary integration. AgentCraft works by installing lightweight hooks into Claude Code that report session events to the server.

## How It Works

AgentCraft installs event hooks into ~/.claude/settings.json. These hooks fire shell scripts that send events (hero spawn, active, idle, file access, etc.) to the AgentCraft server via HTTP.

### Hook Events

| Event | Trigger | Purpose |
| --- | --- | --- |
| SessionStart | New Claude Code session | Spawn a hero on the map |
| UserPromptSubmit | User sends a prompt | Hero becomes active |
| Stop | Session stops | Hero goes idle |
| PreToolUse (Task) | Subagent spawned | Track subagent on map |
| PreToolUse (Read/Write/Edit) | File operations | Track file access |
| PreToolUse (AskUserQuestion) | Agent asks a question | Hero enters "awaiting input" state |
| SubagentStop | Subagent finishes | Update subagent status |
| PermissionRequest | Agent needs approval | Hero glows yellow |

## Hero Types

### External Heroes

Start a Claude Code session in any terminal while AgentCraft is running:

```
claude
```

The session is automatically detected via hooks and appears on the map. Everything you do in that terminal is reflected in real time.

### Internal Heroes

Press Q at the Town Hall (or in the command grid) to spawn a Claude Code hero directly from the UI. Internal heroes run in the background and you interact with them entirely through the game interface.

## Features

Claude Code heroes support all AgentCraft features:

- Real-time conversation via the Side Panel
- Plan review and approval workflow
- Permission request handling (tool use approvals)
- File operation tracking
- Git diff viewing
- Model selection (Opus, Sonnet, Haiku, or custom)
- Fork and handoff to other heroes
- Agent Teams support
- Subagent tracking

## Model Selection

Use the model dropdown at the top of the Side Panel to change models per hero:

| Option | Behavior |
| --- | --- |
| Default | No --model flag (recommended for Bedrock/Vertex) |
| Opus | --model opus |
| Sonnet | --model sonnet |
| Haiku | --model haiku |
| Custom | Any model string (e.g., ollama:llama3) |

The system auto-syncs the displayed model with the one actually being used.