---
title: OpenClaw Integration
url: https://www.getagentcraft.com/docs/integrations/openclaw
fetched: 2026-05-04
type: documentation
---

# OpenClaw

Experimental passive integration with OpenClaw agents.

AgentCraft supports OpenClaw as an experimental passive monitoring integration alongside Claude Code, OpenCode, and Cursor.

## How It Works

Unlike other integrations, OpenClaw is read-only — AgentCraft cannot spawn or control OpenClaw agents. Instead, OpenClaw agents self-report their activity by POSTing events to AgentCraft's /event endpoint. This lets them appear on the 3D map, hero roster, and dashboard alongside your other agents.

AgentCraft installs a SKILL.md file into your OpenClaw workspace during setup. This skill instructs the agent to report key events (active, idle, mission start, file access, bash commands) to the AgentCraft server automatically.

You can also install the skill manually. Tell your OpenClaw agent to read and install the skill file:

```
Read https://app.agentcraft.gg/skills/openclaw.md and follow the instructions to visualize your actions in AgentCraft
```

## Setup

If OpenClaw is installed (~/.openclaw/ directory or openclaw CLI on PATH), AgentCraft automatically installs the reporting skill during setup:

```
npx @idosal/agentcraft install
```

For reliable always-on reporting, add the following to your OpenClaw SOUL.md:

```
## AgentCraft Status Sync
- Before starting any task: run the agentcraft skill to ensure the server is running, then POST hero_active + mission_start
- After finishing any task: POST hero_idle
- Silently ignore POST errors (server may not be running)
```

## Reported Events

| Event | When |
| --- | --- |
| hero_active | Agent starts processing a prompt |
| mission_start | New task begins |
| file_access | File read/write/edit |
| bash_command | Shell command execution |
| hero_idle | Agent finishes and awaits next prompt |

## Limitations

- Experimental — OpenClaw support is new and may have rough edges
- Passive only — AgentCraft cannot spawn, fork, or control OpenClaw agents
- No plan approval or permission handling — These are Claude Code-specific features
- Events are fire-and-forget — the agent silently ignores failures if AgentCraft isn't running