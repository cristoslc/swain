---
title: Agent Teams
url: https://www.getagentcraft.com/docs/features/agent-teams
fetched: 2026-05-04
type: documentation
---

# Agent Teams

Run collaborative multi-agent team workflows.

Agent Teams let you run a team lead with multiple teammates — all visible and manageable from the AgentCraft UI.

## Setup

1. Enable in settings — Go to Settings > Game tab and turn on Agent Teams.
2. Configure teams — Claude Code stores team configs at ~/.claude/teams/{team-name}/config.json. Each config defines a lead agent and a list of teammates.
3. Install tmux (recommended) — With tmux, each teammate gets its own process, hooks, and independent session tracking. Without it, teammates run in-process inside the lead and have limited visibility.

## How It Works

One Claude Code session acts as the team lead (orchestrator) and spawns N teammates. When Agent Teams are enabled, AgentCraft sets CLAUDE_CODE_SPAWN_BACKEND=tmux so teammates get independent processes with their own hook events and session tracking.

Without tmux installed, Claude Code automatically falls back to in-process mode. Teammates still appear in the UI via virtual sessions and task-file-based activity detection, but with reduced visibility.

## UI Indicators

### Agent Status Panel

- Team members are grouped together with a colored left border
- The team lead is marked with a star badge
- Each team member shows their latest inbox message or task description at a glance

### 3D Map and Minimap

- Each team member gets a colored ring on the ground beneath them on the 3D map
- The same colored ring appears on the minimap
- Color is derived from the team name

### Side Panel

For virtual team members (teammates without their own Claude session), the Side Panel shows inbox messages — messages sent between teammates and the lead.

## Team Banners

Customize team colors and banner icons in Settings > Game tab > Team Banners.

## How Sessions Are Detected

AgentCraft uses multiple detection mechanisms:

1. Team config scanning — The server polls ~/.claude/teams/ every ~15 seconds to discover team configurations
2. Hook forwarding — Shell hooks send team_member_detected events when team environment variables are present
3. Virtual sessions — For in-process teammates that don't create their own Claude sessions, the server synthesizes virtual session objects using task files and lead-active inference
4. Task file activity — ~/.claude/tasks/{team-name}/*.json files indicate what each teammate is working on

## Notes

- The team scanner always runs regardless of the toggle — external CLI sessions might have teams even if the game UI hasn't enabled it
- The toggle only controls whether internal heroes (spawned from the UI) can form teams
- Team member names from the config take priority over auto-generated hero names