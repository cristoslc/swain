---
title: Side Panel
url: https://www.getagentcraft.com/docs/features/side-panel
fetched: 2026-05-04
type: documentation
---

# Side Panel

The primary interface for interacting with individual agents.

The Side Panel is AgentCraft's primary interface for interacting with individual agents. Press Enter with a hero selected to open it.

## Tabs

The Side Panel has three tabs:

| Tab | Purpose |
| --- | --- |
| Chat | Real-time conversation, tool use blocks, thinking blocks, file operations |
| Git | View file changes and per-file diffs |
| Files | Browse the project directory tree with search |

## Chat Tab

### Message Types

- User messages — Your prompts, displayed on the right
- Assistant messages — Agent responses with full markdown rendering
- Tool use blocks — Shows tool name and arguments (Read, Write, Edit, Bash, etc.)
- Thinking blocks — The agent's reasoning process

### Streaming

Agent responses stream in real time via WebSocket. The operation ticker at the bottom shows what the agent is currently doing:

- "Reading App.tsx"
- "Editing config.json"
- "Running git status..."
- "Searching for pattern..."

### Scroll Behavior

- Auto-scrolls to the bottom when new messages arrive (if you're already near the bottom)
- Shows a "new content" badge when messages arrive while you're scrolled up
- Scroll-to-top and scroll-to-bottom buttons for quick navigation

## Agent Vitals Header

The top of the Side Panel shows:

- Hero name — Click to rename
- Model selector — Dropdown to change the agent's model mid-session
- Context usage bar — Green (< 70%), yellow (70-90%), red (> 90%)
- Current activity — Active mission name or "Idle"
- Last completed mission — Summary of the most recent finished task

## Composer

The message input area at the bottom of the panel.

### File Autocomplete

Type @ followed by a filename to trigger file autocomplete. The dropdown shows matching files from your project:

- Arrow keys to navigate suggestions
- Enter to select a file
- Escape to close the dropdown

### Sending

Press Cmd+Enter (or Ctrl+Enter) to send your message.

### External Sessions

For external heroes (started in a separate terminal), the composer shows:

- Fork Session button — Forks the external session into a new internal hero
- New Hero button — Navigates to Town Hall to spawn a fresh hero

## Plan Review

When an agent enters plan mode, the Side Panel switches to a full-screen plan review:

- Markdown rendering with syntax highlighting
- File paths highlighted in gold (e.g., src/App.tsx:123)
- Sections dropdown for navigating multi-section plans
- Scroll progress bar showing your position in the document
- Feedback textarea to request plan modifications
- Toggle to switch between plan view and conversation

## Permission Requests

When an agent needs tool approval:

- The hero glows yellow on the map
- The Side Panel shows the tool name and arguments
- Press Y to approve, N to deny
- The composer is disabled during permission review

## Git Tab

The Git tab opens the Codex — a viewer showing pending codebase changes across all sessions:

- Files grouped by directory
- Search by file name or path
- Filter by hero (session)
- Status labels: altered, sealed, newly scribed, destroyed
- Click a file to view its diff

## Handoff and Fork Citations

When a hero was created via handoff or fork, the chat shows a citation linking back to the source hero with their portrait.