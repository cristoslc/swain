---
title: "Claude Code Context Window: Optimize Your Token Usage (ClaudeFast)"
source-id: claudefast-context-management
url: "https://claudefa.st/blog/guide/mechanics/context-management"
type: web-page
fetched: 2026-04-15
transcript-source: manual
---

# Claude Code Context Window — Context Management Guide

Source: ClaudeFast guide on context window management.

## Key finding: Compaction reads session memory, does not re-summarize

Direct quote from the article: "Compaction is fast because Claude maintains a
continuous session memory in the background, so compaction loads that summary
into a fresh context rather than re-summarizing from scratch."

This confirms that `/compact` reads the pre-written `summary.md` rather than
invoking the conversation-summarization agent prompt on the full history.
The agent prompt exists as a fallback or for the first compaction before
session memory exists.

## Session memory location

Session memory files live at:
`~/.claude/projects/<project-hash>/<session-id>/session_memory/`

Each session gets its own directory with its own `summary.md`. These accumulate
over time, building a history of work on each project.

## Compaction threshold

Auto-compaction triggers "around 80-90% context utilization" (exact threshold
varies by CLI version; can be overridden with `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`).

## Implication for /recap

If `/compact` reads session memory instead of re-summarizing, and `/recap` uses
the same session memory infrastructure (which the absence of a new prompt in
v2.1.108 strongly suggests), then `/recap` is architecturally a read of the
pre-written `summary.md` with an injection into the current context — not a
model generation step.

The `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` env var likely forces the injection
even when telemetry (which normally detects the "away" state) is disabled.
