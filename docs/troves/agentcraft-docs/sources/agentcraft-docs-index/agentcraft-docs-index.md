---
title: AgentCraft Documentation
url: https://www.getagentcraft.com/docs
fetched: 2026-05-04
type: documentation
---

# AgentCraft Documentation

**Source:** https://www.getagentcraft.com/docs

**Summary:** AgentCraft is an open-source tool that reimagines how you interact with AI coding agents. Instead of a plain terminal, you get a full RTS-style command center where each AI agent is a hero unit on a 3D map, complete with missions, fog of war, skill scrolls, and achievements.

## What is AgentCraft?

AgentCraft transforms your AI coding workflow into a real-time strategy experience. Watch your agents come alive in an RTS game interface — track and summon agents and subagents, command them, and manage them. Recycle with the intuitive interface you know and love.

AgentCraft works by installing lightweight hooks into your agent CLI (Claude Code, OpenCode, or Cursor). These hooks report session events to the AgentCraft server, which renders everything in a browser-based game UI.

## Key Features

- **Multi-Agent Heroes** — Each AI agent appears as a hero on the map with real-time status tracking
- **Agent Teams** — Display Claude Code team configurations with grouped parties
- **Alliance Hall** — Collaborative multiplayer: create a shared room and see remote agents from other developers on your map in real time
- **Mission Tracking** — Completed missions persist across restarts with AI-generated summaries
- **Fog of War** — Toggle with V to visualize which areas have active heroes
- **Skill Scrolls** — Collectible scrolls on the map that install real agent skills from skills.sh
- **Achievements** — Tiered unlock system with shareable trophy cards
- **Channels** — DM your heroes from Telegram or Discord to send prompts, approve plans, and grant permissions
- **Remote Access & Mobile** — Secure tunnel sharing with installable mobile PWA and push notifications
- **Voice Input** — Speech-to-text in the composer with auto-send on silence
- **Isolated Containers** — Run agents in Docker or Apple Containers with full network isolation
- **Scheduled Tasks** — Create recurring agent tasks with cron-like intervals
- **Integrated Terminal** — Full PTY terminal in the bottom HUD with multi-tab support
- **File Explorer** — Browse project files in the side panel with search and IDE integration
- **Git Worktrees** — Spawn heroes in different worktrees directly from the UI
- **Git Management** — Built-in stash and branch management
- **Music** — Ambient soundtrack toggle
- **Race Skins** — Choose between Orc, Human, Elf, and Undead factions with unique buildings, heroes, terrain, and portraits

## Quick Start

Run the following command:

```
npx @idosal/agentcraft
```

This runs the guided setup: detects your agent CLIs, installs hooks, starts the server on port 2468, and opens the browser UI.

## Supported Agents

- **Claude Code** — Full integration with Anthropic's CLI agent (primary)
- **OpenCode** — 75+ models from multiple providers
- **Cursor** — Cursor's agent mode via CLI
- **OpenClaw** — Experimental

## Community

- **Discord** — Get help and share feedback: https://discord.gg/nEaZAH7C7F
- **Twitter / X** — Follow for updates: https://x.com/idosal1