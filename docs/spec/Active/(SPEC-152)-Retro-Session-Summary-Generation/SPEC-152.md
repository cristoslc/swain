---
title: "swain-retro: session summary generation"
artifact: SPEC-152
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: ""
type: enhancement
parent-epic: EPIC-042
parent-initiative: ""
linked-artifacts:
  - EPIC-042
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

**Input:** Scrubbed JSONL (from retro folder, decompressed if needed) + swain-session bookmarks from `.agents/session.json`

**Output:** `session-summary.md` in the retro folder with this structure:

```markdown
# Session Summary

## Decision Points
- [Brief description of each moment where the agent chose between alternatives]

## Pivot Points
- [Moments where the approach changed — failed tool calls, user corrections, strategy shifts]

## Surprises
- [Unexpected outcomes — things that worked against expectations, blockers, scope discoveries]

## Learnings
- [Process insights — what the session reveals about workflow effectiveness]

---

## Chronological Narrative

### [Bookmark: "Started SPEC-042 implementation"] (14:30)
[What happened in this segment — tool calls, decisions made, outcomes]

### [Bookmark: "Pivoted from approach A to B"] (14:45)
[What happened in this segment]
```

**Bookmark fallback:** If `.agents/session.json` has no bookmarks or swain-session isn't installed, the narrative uses time-based chunking (~15-minute windows of session activity).

**Token management:** If the scrubbed JSONL exceeds ~200K tokens, the skill processes it in chronological chunks (bounded by bookmarks or 15-minute windows), generating per-chunk summaries that are synthesized into the final session-summary.md.

**Generation method:** Agent-generated (LLM reasoning at retro time), not scripted heuristics. The four top-level sections require interpretive analysis of the session's decision flow.

**Manifest update:** After generating, update the retro manifest's `summary` section with `generated: true`, `bookmark-count`, and counts for each of the four categories.

## Acceptance Criteria

- Given a retro folder with a scrubbed JSONL archive, when session summary is generated, then `session-summary.md` exists in the folder
- Given the generated session-summary.md, then it contains all four top-level sections: `## Decision Points`, `## Pivot Points`, `## Surprises`, `## Learnings`
- Given the generated session-summary.md, then it contains a `## Chronological Narrative` section with at least one subsection
- Given swain-session bookmarks exist, then the chronological narrative sections reference bookmark labels
- Given no bookmarks exist, then the chronological narrative uses time-based sections (~15-minute intervals) and the summary is still generated
- Given a retro manifest exists, then after summary generation the `summary.generated` field is `true` and category counts are populated
- Given the session summary is generated, then it does not reproduce raw JSONL content — it summarizes actions, decisions, and outcomes in narrative form

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Output is LLM-generated and non-deterministic. Acceptance criteria verify structural completeness (sections present, chronological ordering, bookmark references) but not content quality. Content quality is verified by operator review.
- The summary should not exceed ~2000 words for a typical session. Longer sessions may produce longer summaries but should prioritize signal density over completeness.
- No new scripts — this is skill behavior added to swain-retro SKILL.md

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | — | Initial creation |
