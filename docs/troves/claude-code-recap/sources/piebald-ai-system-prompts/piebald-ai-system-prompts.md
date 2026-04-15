---
title: "Claude Code System Prompts — Extracted from Source (Piebald-AI)"
source-id: piebald-ai-system-prompts
url: "https://github.com/Piebald-AI/claude-code-system-prompts"
type: web-page
fetched: 2026-04-15
transcript-source: manual
---

# Claude Code System Prompts — Extracted from Source

Repository maintained by Piebald-AI. Extracts all system prompts and agent
prompts directly from Claude Code's compiled npm bundle, updated per release.
At time of research: tracking v2.1.108.

## Key finding: No new recap-specific prompt in v2.1.108

The v2.1.108 changelog entry for this repo records only REPL tool guidance
updates and minor prompt edits — no new "recap" or "away summary" agent prompt
was added. This means `/recap` does not use a dedicated summarization prompt.
It reuses the existing session memory infrastructure.

## Relevant prompts (pre-existing, v2.1.84)

### agent-prompt-conversation-summarization

Used by `/compact`. Instructs Claude to produce a detailed session summary
covering: primary request and intent, key technical concepts, files and code
sections, errors and fixes, problem solving, all user messages, pending tasks,
current work, and optional next step.

This is a full-session summarization prompt — it processes the entire
conversation history and produces a structured document.

### agent-prompt-recent-message-summarization

Variant of the above. Summarizes only the recent portion of a conversation
after a retained earlier context block. Used when partial compaction is
requested.

### data-session-memory-template

Template structure for the `summary.md` file maintained continuously in the
background at `~/.claude/projects/<project-hash>/<session-id>/session_memory/`.

Sections:
- Session Title (5-10 word descriptor)
- Current State (what is actively being worked on, pending tasks, next steps)
- Task Specification (what the user asked to build, design decisions)
- Files and Functions (important files, their contents, relevance)
- Workflow (bash commands, output interpretation)
- Errors & Corrections (errors encountered, user corrections, failed approaches)
- Codebase and System Documentation (system components, how they fit together)
- Learnings (what worked, what failed, what to avoid)
- Key Results (exact output if user asked a specific question)
- Worklog (terse step-by-step log of what was attempted/done)

### agent-prompt-session-memory-update-instructions

Instructs Claude to update the `summary.md` file continuously during sessions.
Key constraint: always update "Current State" for continuity. Never modify
section headers or template lines. Keep content under a token limit
(`MAX_SECTION_TOKENS`). Primary instruction: "Your ONLY task is to use the
Edit tool to update the notes file, then stop."

## Inference: How /recap works

Given that:
1. No new summarization prompt exists for `/recap` in v2.1.108
2. Session Memory (`summary.md`) is maintained continuously in the background
3. `/compact` is confirmed to read pre-written session memory (not re-summarize live)

The most coherent explanation is that `/recap` injects the existing
`summary.md` content as a briefing when the operator returns — without
replacing conversation history. The "away" detection (via telemetry or
`CLAUDE_CODE_ENABLE_AWAY_SUMMARY`) determines *when* to inject, not *what* to
generate. The content is already there.
