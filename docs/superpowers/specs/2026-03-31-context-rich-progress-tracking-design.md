# Context-Rich Progress Tracking

## Problem

Swain surfaces opaque artifact IDs everywhere — status dashboards, recommendations, roadmaps, retro summaries. The operator must context-switch to remember what each ID means, why it matters, and where it stands. This cognitive load compounds as the project grows. There is no mechanism to capture what a session accomplished or to accumulate progress toward higher-level goals.

## Goal

Every time swain shows an artifact to the operator, it carries enough context that the operator never has to look it up. And that context is grounded in actual session evidence, not just artifact state counts.

## Design

### Layer 1: Session Digest

At session close, swain-session auto-generates a structured digest. No operator interaction needed.

**Evidence sources:**
- Git log (commits since session start)
- tk task completions (claimed, closed, abandoned)
- Artifact transitions (phase changes detected by comparing artifact state at session start vs. end)

**Storage:** One JSONL entry per session in `.agents/session-log.jsonl`.

**Schema:**
```json
{
  "session_id": "session-20260330-222903-eef9",
  "timestamp": "2026-03-31T02:30:00Z",
  "focus_lane": "INITIATIVE-019",
  "artifacts_touched": [
    {
      "id": "SPEC-194",
      "title": "Flesch-Kincaid Readability Enforcement",
      "action": "implemented",
      "summary": "Script, governance rule, and protocol doc shipped. All 17 tests pass."
    }
  ],
  "commits": 7,
  "tasks_closed": 7,
  "session_summary": "Implemented readability enforcement end-to-end and released v0.23.0-alpha."
}
```

**Trigger:** Fires automatically at session close (swain-session close step). For autonomous sessions that don't go through a formal close, the next session's startup can generate a retroactive digest from the previous session's evidence.

### Layer 2: Progress Log

Each EPIC and Initiative gets a `progress.md` file in its artifact directory.

**Example path:** `docs/epic/Active/(EPIC-048)-Session-Startup-Fast-Path/progress.md`

**Format:**
```markdown
# Progress Log

## 2026-03-30
Completed SPIKE-001 timing instrumentation. Baseline measurements show 4.2s startup. Discovered specgraph import bug (SPEC-197) adding ~800ms. 4 implementation specs planned, none started.

## 2026-03-29
Created epic and decomposed into 4 specs + 1 spike. Spike activated for baseline timing.
```

**Update mechanism:** After generating a session digest, swain-retro reads `artifacts_touched` and appends a dated entry to each referenced artifact's progress log. Each entry is 2-3 sentences: what happened and what it means for the goal.

### Layer 3: Progress Synthesis

Each EPIC and Initiative gets a `## Progress` section in the artifact itself. This is not a growing log — it is a living summary that replaces itself each time the progress log is updated.

**Example:**
```markdown
## Progress

Spike complete with baseline measurements (4.2s startup). Root cause identified: specgraph import shadowing adds ~800ms. 4 implementation specs planned across bootstrap optimization, worktree deferral, init chain collapse, and the import fix. None started yet.
```

**Generation:** After appending to the progress log, swain-retro reads the full log and synthesizes a current-state summary. It replaces the previous `## Progress` content entirely. The synthesis answers three questions: what's done, what's in flight, and what's left.

**Consumer:** swain-session reads this section when building operator-facing output. It is the single source of truth for "how is this artifact going?"

### Context-Rich Display

A shared utility takes an artifact ID and returns a context line for operator-facing output.

**Format:**
```
**{title}** `{ID}` — {scope sentence}. {progress clause}.
```

Title leads bold (prominent). ID in code font (secondary/dimmed). Scope comes from the first sentence of the Problem Statement or Goal section. Progress clause comes from the `## Progress` section, or falls back to child artifact counts from specgraph.

**Examples:**

> **Readability enforcement** `SPEC-194` — deterministic FK scoring for all artifacts. All 3 deliverables shipped, released in v0.23.0-alpha.

> **Session startup fast path** `EPIC-048` — reduce session boot time below 3 seconds. Spike complete, 4 specs planned, none started.

> **Operator cognitive support** `VISION-004` — help the operator maintain focus and recover context. 2 of 5 initiatives active, 1 complete.

**Integration points:**

| Surface | Owner skill | What changes |
|---------|-------------|-------------|
| Status dashboard | swain-session | Recommendations use context lines instead of bare IDs |
| "What's next?" | swain-session | Ranked list uses context lines |
| Roadmap | swain-roadmap | Gantt/quadrant items carry plain-language labels + progress |
| Retro summaries | swain-retro | Referenced artifacts use context lines |
| Scope checks | swain-design | Ancestry chains use plain-language names |
| Focus lane display | swain-session | Focus shown as context line, not bare ID |

**Implementation:** A script (`artifact-context.sh` or Python equivalent) in `.agents/bin/` that:
1. Reads frontmatter `title` field
2. Reads the first sentence of `## Problem Statement` or `## Goal`
3. Reads `## Progress` section if it exists
4. Falls back to specgraph child artifact counts if no progress section
5. Returns a formatted context line

Every skill that displays artifacts to the operator calls this utility instead of printing bare IDs.

### Template Changes

- EPIC template gains an empty `## Progress` section (populated by first session digest)
- Initiative template gains an empty `## Progress` section
- New file convention: `progress.md` alongside EPIC and Initiative artifacts (created on first session digest that touches the artifact)

### What This Does NOT Do

- Does not change artifact lifecycle phases or transitions
- Does not require operator input at session close
- Does not retroactively generate progress logs for existing artifacts (can be done as a one-time sweep later)
- Does not replace the existing EPIC `## Retrospective` section (retros are terminal reflections; progress is ongoing)
- Does not modify specgraph queries — it layers context on top of existing outputs

### Relationship to EPIC-042

EPIC-042 (Retro Session Intelligence) is already planning deeper session provenance for retros. This design is complementary: EPIC-042 focuses on making retros richer by capturing session JSONL archives. This design focuses on making all operator-facing output context-rich by accumulating progress and displaying it. The session digest (Layer 1) could serve both — EPIC-042's session summaries and this design's progress log entries could read from the same JSONL source.
