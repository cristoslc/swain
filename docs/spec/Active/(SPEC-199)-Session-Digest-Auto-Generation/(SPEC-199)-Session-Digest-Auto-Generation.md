---
title: "Session Digest Auto-Generation"
artifact: SPEC-199
track: implementable
status: Active
author: Cristos L-C
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: feature
parent-epic: EPIC-049
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Session Digest Auto-Generation

## Problem Statement

When a session ends, the evidence of what happened (commits, task completions, artifact transitions) is scattered across git log, tk, and artifact files. No single record captures what the session accomplished. Without this, progress tracking has no raw material to work with.

## Desired Outcomes

Every session produces a structured digest that records what changed, which artifacts were touched, and a brief summary. This accumulates in a single JSONL file that any skill can query.

## External Behavior

At session close (swain-session close step), the agent reads:
- Git log since session start (commits)
- tk task completions (closed tasks tagged with spec IDs)
- Artifact transitions (phase changes in docs/)

It writes one JSONL entry to `.agents/session-log.jsonl` with this schema:

```json
{
  "session_id": "session-20260330-222903-eef9",
  "timestamp": "2026-03-31T02:30:00Z",
  "focus_lane": "INITIATIVE-019",
  "artifacts_touched": [
    {
      "id": "SPEC-203",
      "title": "Flesch-Kincaid Readability Enforcement",
      "action": "implemented",
      "summary": "Script, governance rule, and protocol doc shipped."
    }
  ],
  "commits": 7,
  "tasks_closed": 7,
  "session_summary": "Implemented readability enforcement and released v0.23.0-alpha."
}
```

For autonomous sessions that skip formal close, the next session's startup generates a retroactive digest from the previous session's evidence.

Zero operator interaction required.

## Acceptance Criteria

1. **Given** a session with commits and task completions, **when** the session closes, **then** a JSONL entry is appended to `.agents/session-log.jsonl`.

2. **Given** the JSONL entry, **when** read by another tool, **then** it contains session_id, timestamp, focus_lane, artifacts_touched (with id, title, action, summary), commits count, tasks_closed count, and session_summary.

3. **Given** an autonomous session that ended without formal close, **when** the next session starts, **then** a retroactive digest is generated from the previous session's evidence.

4. **Given** a session with no artifact changes (e.g., pure research), **when** the session closes, **then** a digest is still generated with empty artifacts_touched and a summary reflecting what happened.

5. **Given** the digest generation step, **when** it runs, **then** it completes with zero operator interaction.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- In scope: digest generation script, swain-session close integration, retroactive digest on startup
- Out of scope: reading or consuming the digest (that's SPEC-200 and SPEC-202)
- The JSONL file lives in `.agents/` (not committed to git — session-local ephemeral data)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | _pending_ | Initial creation |
