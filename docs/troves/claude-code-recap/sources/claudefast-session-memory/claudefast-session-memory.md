---
title: "Claude Code Session Memory: How Your AI Remembers Across Sessions"
source-url: "https://claudefa.st/blog/guide/mechanics/session-memory"
source-type: web-page
fetched: 2026-04-14
transcript-source: convert-to-markdown
---

# Claude Code Session Memory: How Your AI Remembers Across Sessions

**Source:** claudefa.st
**Relevance to /recap:** Session Memory is a distinct, older feature. Understanding it clarifies what /recap is NOT.

## What Session Memory Is

Session Memory is Claude Code's automatic background system for remembering what you did **across sessions**. Unlike CLAUDE.md (which you write manually), Session Memory runs without input. It watches your conversation, extracts important parts, and saves structured summaries to disk.

Terminal messages:
- **"Recalled X memories"** — appears at session start; Claude loaded summaries from previous sessions.
- **"Wrote X memories"** — appears periodically; Claude saved a snapshot of current work.

## How It Works

**Storage location:**
```
~/.claude/projects/<project-hash>/<session-id>/session-memory/summary.md
```

**Extraction cadence:**
- First extraction: after ~10,000 tokens of conversation.
- Subsequent updates: every ~5,000 tokens or after every 3 tool calls.

**Cross-session recall:** When starting a new session, Claude injects relevant past session summaries into context, tagged as "from PAST sessions that might not be related to the current task." Used as background reference, not active instructions.

## What Gets Remembered

Each summary includes:
- **Session title** — auto-generated description of work done.
- **Current status** — completed items, discussion points, open questions.
- **Key results** — outcomes, decisions made, patterns chosen.
- **Work log** — chronological record of actions.

## The /remember Command

`/remember` converts session memory into permanent project knowledge. It reviews stored summaries, identifies recurring patterns, and proposes updates to `CLAUDE.local.md`. You confirm each addition.

## Instant Compaction

Session Memory enables instant `/compact`. Previously, compaction took up to two minutes to re-analyze the conversation. Now compaction loads the pre-written summary immediately. The summary is always ready.

## Availability

- Available on first-party Anthropic API (Pro/Max subscriptions). Not available on Bedrock, Vertex, or Foundry.
- Feature-flagged: `tengu_session_memory` for core feature, `tengu_sm_compact` for instant compaction.
- Underlying system exists since ~v2.0.64 (late 2025). Visible terminal messages became prominent ~v2.1.30–v2.1.31 (February 2026).

## Session Memory vs. /recap (Key Distinction)

| Feature | Session Memory | /recap |
|---------|---------------|--------|
| Trigger | Automatic, background | On-demand (`/recap`) or auto on return |
| Scope | Cross-session (yesterday → today) | Within-session (stepped away → came back) |
| Storage | `~/.claude/projects/.../session-memory/` | Ephemeral (no persistent file) |
| Availability | First-party API only | All plans (with telemetry override) |

Session Memory answers "What did we do last week?" `/recap` answers "What were we doing before I stepped away?"

## CLAUDE.md vs. Session Memory vs. /recap

| Aspect | Session Memory | CLAUDE.md | /recap |
|--------|---------------|-----------|--------|
| Created by | Claude (automatic) | You (manual) | Claude (on return/demand) |
| Scope | Per-session snapshots | Persistent project rules | In-session away context |
| Best for | Continuity across days | Standards, architecture | Re-orientation after break |
