---
title: "Claude Code Changelog — Recap-Adjacent Entries"
source-url: "https://code.claude.com/docs/en/changelog"
source-type: web-page
fetched: 2026-04-14
transcript-source: convert-to-markdown
---

# Claude Code Changelog — Recap-Adjacent Entries

**Source:** Official Claude Code changelog
**Purpose:** Surrounding changelog entries that provide timeline and context for the /recap feature.

## v2.1.108 — April 14, 2026 (Recap Introduction)

Full entry: see `claude-code-releases-v2-1-108` source. Primary change:

> Added recap feature to provide context when returning to a session, configurable in `/config` and manually invocable with `/recap`; force with `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` if telemetry disabled.

Key configuration detail: the env var name `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` is significant — it names the underlying mechanism "away summary," confirming the feature triggers when the user has been **away** from an active session.

## v2.1.69 — March 5, 2026 (Preamble Removal)

> Changed resuming after compaction to no longer produce a preamble recap before continuing.

Prior to this: when a session resumed after compaction, Claude would automatically emit a "here's what happened" preamble. This was removed in v2.1.69, six weeks before the dedicated `/recap` command landed. The decision to remove the compaction preamble likely preceded the more deliberate `/recap` feature design.

## v2.1.68 — March 4, 2026 (Model Defaults)

- Opus 4.6 now defaults to medium effort for Max and Team subscribers.
- Re-introduced "ultrathink" keyword to enable high effort for the next turn.
- Removed Opus 4 and 4.1 from Claude Code on the first-party API.

## v2.1.87 — March 29, 2026 (Session Resume Improvements)

> Improved `/resume` picker to show your most recent prompt instead of the first one.

Part of a series of session-continuity improvements preceding the /recap launch.

## v2.1.83 — March 25, 2026 (Memory Footprint)

- Reduced memory usage when resuming large sessions (including compacted history).
- Reduced token usage on multi-agent tasks with more concise subagent final reports.
- Changed `example command suggestions` to be generated deterministically instead of calling Haiku.

## Pattern: Session Continuity Trajectory

From the changelog, a clear trajectory of session-continuity improvements leading to /recap:

1. **v2.0.64 (late 2025)** — Session Memory background summaries introduced.
2. **v2.1.30–2.1.31 (February 2026)** — Session Memory "Recalled/Wrote memories" messages become visible.
3. **v2.1.69 (March 5, 2026)** — Compaction preamble recap removed (simplified post-compaction resume).
4. **v2.1.87 (March 29, 2026)** — `/resume` picker shows most recent prompt (better re-orientation).
5. **v2.1.108 (April 14, 2026)** — `/recap` command introduced for active-session return context.
