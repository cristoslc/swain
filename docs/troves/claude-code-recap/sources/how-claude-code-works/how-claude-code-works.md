---
title: "How Claude Code Works — Sessions and Context Window"
source-url: "https://code.claude.com/docs/en/how-claude-code-works"
source-type: web-page
fetched: 2026-04-14
transcript-source: convert-to-markdown
---

# How Claude Code Works — Sessions and Context Window

**Source:** Official Claude Code documentation
**Relevance to /recap:** Canonical reference for session lifecycle, context management, and compaction — the infrastructure /recap builds on.

## Sessions

Claude Code saves conversations locally as JSONL files under `~/.claude/projects/`. This enables rewinding, resuming, and forking sessions.

**Sessions are independent.** Each new session starts fresh. Claude can persist learnings via auto memory and CLAUDE.md.

### Resume or Fork

- `claude --continue` — picks up the last session for the current directory.
- `claude --resume` — opens a picker to choose any past session.
- `claude --continue --fork-session` — creates a new session branching from the current history.

Resuming restores conversation history but NOT session-scoped permissions (those require re-approval).

**Warning:** Resuming the same session in multiple terminals causes interleaved writes. Use `--fork-session` for parallel work.

### Context Window Contents

The context window holds:
- Conversation history
- File contents
- Command outputs
- CLAUDE.md
- Auto memory (first 200 lines or 25KB of MEMORY.md)
- Loaded skills
- System instructions

Run `/context` to see what is using space.

### When Context Fills Up

Claude Code manages context automatically:
1. Clears older tool outputs first.
2. Summarizes the conversation if needed.
3. Preserves recent requests and key code snippets; may lose early instructions.

**Tip:** Put persistent rules in CLAUDE.md. Use `/compact [instructions]` to manually trigger with preservation guidance.

If a single file or output causes context to refill immediately after summary, Claude Code stops auto-compacting and shows a thrashing error.

### Context Cost of Features

- **Skills** — load descriptions at start, full content only on use.
- **Subagents** — get their own fresh context, return only a summary.
- **MCP tools** — deferred by default; only tool names consume context until used.

## Memory Features (Relevant Context for /recap)

Three memory layers exist:

1. **CLAUDE.md** — manually maintained, high-priority, loads every session.
2. **Auto memory** — Claude writes notes automatically to MEMORY.md. Loads first 200 lines/25KB at start.
3. **Session Memory** — background summaries written per session, recalled at next session start.

The `/recap` feature (v2.1.108) adds a fourth mode: **in-session away context** — a summary generated when you return to an active session after stepping away.

## Compaction

`/compact` summarizes the current conversation and starts fresh with that summary preloaded. Can be run manually or triggered automatically at ~95% context usage.

Custom compaction focus: `/compact focus on the API changes`

Or add a "Compact Instructions" section to CLAUDE.md for automatic guidance.
