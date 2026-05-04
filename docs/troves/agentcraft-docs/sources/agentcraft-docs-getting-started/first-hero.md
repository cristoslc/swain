---
title: Your First Hero
url: https://www.getagentcraft.com/docs/getting-started/first-hero
fetched: 2026-05-04
type: documentation
---

# Your First Hero

Spawn and interact with your first AI agent hero.

Each AI agent in AgentCraft appears as a hero on the 3D map. Heroes can be spawned from the UI or detected automatically from external terminal sessions.

## Spawn a Hero

Use the Town Hall command grid at the bottom of the screen:

- Press Q to spawn a Claude Code hero
- Press W to spawn an OpenCode hero
- Press E to spawn a Cursor hero

Or click the Town Hall building and select a client from the SpawnModal.

## Interacting with a Hero

### Selection

| Key | Action |
| --- | --- |
| 1-8 | Select hero by priority slot |
| Space | Cycle idle/awaiting heroes (awaiting first) |
| I | Cycle idle heroes only |
| W | Cycle working heroes |
| E | Cycle error heroes |

### Side Panel

Press Enter with a hero selected to open the side panel. This is your primary interface:

- Chat tab — Real-time conversation, tool use blocks, file operations
- Git tab — View file changes and diffs
- Files tab — Browse the project directory tree

### Sending Messages

Type in the composer at the bottom of the side panel. Use @ to trigger file autocomplete — type @ followed by a filename to attach context.

Press Cmd+Enter (or Ctrl+Enter) to send.

### Agent Vitals

The side panel header shows:

- Hero name and model
- Context usage bar — Green (< 70%), yellow (70-90%), red (> 90%)
- Current activity or mission name
- Operation ticker — Real-time status like "Reading App.tsx", "Editing config.json", "Running git status..."

### Permission Requests

When an agent needs approval for a tool use:

- The hero glows yellow on the map
- The side panel shows the tool name and arguments
- Press Y to approve, N to deny

### Model Selection

Use the model dropdown at the top of the side panel to switch models per hero:

- Claude Code: Default, Opus, Sonnet, Haiku, or any custom model string
- OpenCode: Models grouped by provider (Anthropic, OpenAI, Google, Groq, etc.)
- Cursor: auto, sonnet-4, opus-4.1, gpt-5, gemini-3-pro, grok

## Control Groups

| Key | Action |
| --- | --- |
| Ctrl+1-9 | Assign selected hero to control group |
| Shift+Ctrl+1-9 | Add selected hero to control group |
| Alt+1-9 | Recall control group |

## Fork and Handoff

| Key | Action |
| --- | --- |
| H | Handoff work to a new hero (with hero selected) |
| Shift+H | Fork hero with full context |

Both support cross-client provider selection.