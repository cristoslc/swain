# AgentCraft Documentation — Synthesis

## Overview

AgentCraft is an open-source tool that transforms AI coding agent workflows into a real-time strategy (RTS) game interface. It works by installing lightweight hooks into agent CLIs (Claude Code, OpenCode, Cursor) that report session events to a browser-based game UI.

## Key Findings

### Architecture

- **Hooks-based integration** — AgentCraft installs hooks into existing agent CLIs to capture session events
- **Browser-based UI** — Renders agents as heroes on a 3D map in a browser
- **Server architecture** — Runs on port 2468 by default

### Agent Support

| Agent | Status |
|-------|--------|
| Claude Code | Primary integration |
| OpenCode | 75+ models supported |
| Cursor | Via CLI |
| OpenClaw | Experimental |

### Feature Categories

**Core Agent Management:**
- Multi-Agent Heroes with real-time status
- Agent Teams with grouped parties
- Mission Tracking with persistence
- Fog of War visualization

**Collaboration:**
- Alliance Hall for multiplayer
- Channels integration (Telegram, Discord)

**Productivity:**
- Integrated Terminal (PTY)
- File Explorer
- Git Worktrees
- Git Management

**Extensibility:**
- Skill Scrolls (installs skills from skills.sh)
- Achievements system
- Scheduled Tasks

**UX:**
- Voice Input
- Race Skins (Orc, Human, Elf, Undead)
- Music
- Remote Access + Mobile PWA

## Points of Agreement

- AgentCraft provides a unique visual approach to agent management
- Multi-agent support is a core feature
- Git integration (worktrees, branch management) is a practical addition for developers

## Gaps

- Pricing model not documented
- Technical architecture details (server components, hook implementation) not covered
- Security model for remote access not detailed