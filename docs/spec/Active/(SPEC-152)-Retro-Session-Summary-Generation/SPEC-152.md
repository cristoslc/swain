---
title: "swain-retro: session summary generation"
artifact: SPEC-152
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
priority-weight: ""
type: enhancement
parent-epic: EPIC-042
parent-initiative: ""
linked-artifacts:
  - EPIC-042
  - SPEC-150
  - SPEC-163
depends-on-artifacts:
  - SPEC-151
addresses: []
evidence-pool: "agent-alignment-monitoring@8047381"
source-issue: ""
swain-do: required
---

# swain-retro: session summary generation

## Problem Statement

Raw session JSONL is dense and hard to navigate. Even with scrubbing and archival (SPEC-151), the transcript is not actionable for agent self-study or operator forensics without a structured summary. The key process alignment signals — decision points, pivots, surprises — are buried in hundreds of tool calls and assistant messages.

## Desired Outcomes

Future agents reading a retro folder can quickly understand *how* a past session navigated decisions by reading `session-summary.md`. Operators can reconstruct decision rationale weeks later without parsing JSONL. The four top-level sections (Decision Points, Pivot Points, Surprises, Learnings) provide a high-level process alignment signal that can be scanned in seconds.

## External Behavior

**Input:** One or more scrubbed JSONL archives from the retro folder (decompressed if needed) + swain-session bookmarks from `.agents/session.json`. A retro may bundle multiple sessions (see SPEC-163 for session discovery).

**Output:** `session-summary.md` in the retro folder — a composite document that synthesizes across all bundled sessions:

```markdown
# Session Summary

## Decision Points
- [Synthesized across all sessions — moments where the agent chose between alternatives]

## Pivot Points
- [Synthesized — strategy shifts, failed tool calls, user corrections]

## Surprises
- [Synthesized — unexpected outcomes, blockers, scope discoveries]

## Learnings
- [Synthesized — process insights across the full arc of work]

---

## Chronological Narrative

### Session abc123 (2026-03-20)

#### [Bookmark: "Started SPEC-150 implementation"] (14:30)
[What happened in this segment — tool calls, decisions made, outcomes]

#### [Bookmark: "Pivoted from approach A to B"] (14:45)
[What happened in this segment]

### Session def456 (2026-03-22)

#### [Bookmark: "Started SPEC-151 implementation"] (10:15)
[What happened in this segment]
```

The four top-level sections synthesize across all sessions — they capture the arc of the work, not just individual session events. The chronological narrative is organized by session (ordered by session start time), with bookmark-based subsections within each.

**Bookmark fallback:** If `.agents/session.json` has no bookmarks or swain-session isn't installed, the narrative uses time-based chunking (~15-minute windows of session activity).

**Token management:** When multiple sessions are bundled, total JSONL can be large. Each session's scrubbed JSONL is processed independently. If a single session exceeds ~200K tokens, it is chunked by bookmarks or 15-minute windows. Per-session summaries are then synthesized into the composite `session-summary.md`.

**Generation method:** Agent-generated (LLM reasoning at retro time), not scripted heuristics. The four top-level sections require interpretive analysis of the decision flow across sessions.

**Manifest update:** After generating, update the retro manifest's `summary` section with `generated: true`, `bookmark-count` (total across sessions), and counts for each of the four categories.

## Acceptance Criteria

- Given a retro folder with one or more scrubbed JSONL archives, when session summary is generated, then `session-summary.md` exists in the folder
- Given the generated session-summary.md, then it contains all four top-level sections: `## Decision Points`, `## Pivot Points`, `## Surprises`, `## Learnings` — synthesized across all sessions
- Given multiple sessions are bundled, then the `## Chronological Narrative` contains a section per session (ordered by session start time) with subsections per bookmark or time window
- Given a single session is bundled, then the chronological narrative still uses the per-session heading structure for consistency
- Given swain-session bookmarks exist, then the chronological narrative subsections reference bookmark labels
- Given no bookmarks exist, then the chronological narrative uses time-based subsections (~15-minute intervals) and the summary is still generated
- Given a retro manifest exists, then after summary generation the `summary.generated` field is `true` and category counts are populated
- Given the session summary is generated, then it does not reproduce raw JSONL content — it summarizes actions, decisions, and outcomes in narrative form

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Output is LLM-generated and non-deterministic. Acceptance criteria verify structural completeness (sections present, chronological ordering, bookmark references) but not content quality. Content quality is verified by operator review.
- Per-session narrative should not exceed ~2000 words. Multi-session summaries scale linearly but top-level synthesis sections should stay concise (~500 words total across the four sections).
- No new scripts — this is skill behavior added to swain-retro SKILL.md
- Multi-session bundling is governed by SPEC-163. This spec owns the summary generation mechanics and output format.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
