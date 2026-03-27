---
title: "Computed Priority Scoring"
artifact: SPEC-161
track: implementable
status: Active
author: cristos
created: 2026-03-23
last-updated: 2026-03-23
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-019
linked-artifacts:
  - SPIKE-042
depends-on-artifacts:
  - SPEC-160
addresses: []
trove: "docs/troves/critical-path-analysis"
source-issue: ""
swain-do: required
---

# Computed Priority Scoring

## Problem Statement

Swain's priority system is static and operator-set: `priority-weight` (high/medium/low) cascades from Vision → Initiative → Epic → Spec, and `chart.sh recommend` uses this weight for sorting. But priority doesn't reflect structural importance — an artifact on the critical path with medium weight should score higher than a high-weight artifact with abundant float. The swain ecosystem extended analysis scored Priority System at 3/5, noting "still operator-set, not computed."

This spec adds a computed urgency score that combines the existing `priority-weight` with critical path analysis ([SPEC-160](../(SPEC-160)-Chart-Critical-Path-Lens/(SPEC-160)-Chart-Critical-Path-Lens.md)), dependency depth, and blocked-count to produce a single sortable score for each artifact.

## Desired Outcomes

`chart.sh recommend` produces a priority-ranked list that reflects both operator intent (priority-weight) and structural reality (critical path, float, blocked count). Agents picking up work via `chart.sh ready` or `chart.sh recommend` get better guidance on what to work on next. The Priority System gap moves from 3/5 toward 4/5.

## External Behavior

**Enhanced subcommand:** `chart.sh recommend` (existing command, new scoring model)

**Inputs:**
- Artifact dependency graph with critical path data (requires SPEC-160)
- `priority-weight` from artifact frontmatter (cascaded)
- Dependency metadata: blocked count (number of artifacts this one gates), float value

**Scoring formula:**

```
urgency = (weight_score × W_WEIGHT)
        + (critical_path_flag × W_CRITICAL)
        + (inverse_float × W_FLOAT)
        + (blocked_count × W_BLOCKED)
```

Where:
- `weight_score`: high=3, medium=2, low=1, unset=2
- `critical_path_flag`: 1 if on critical path, 0 if not
- `inverse_float`: `1 / (float + 1)` — zero float → score 1.0, high float → approaches 0
- `blocked_count`: number of non-terminal artifacts directly depending on this one
- `W_*`: tunable weight constants with sensible defaults (configurable via `.agents/priority-weights.yaml`)

**Outputs:**
- `chart.sh recommend` output includes a `score` column alongside existing fields
- `chart.sh recommend --json` includes `urgency_score` and its component breakdown per artifact
- `chart.sh recommend --explain <ID>` shows the score breakdown for a single artifact

**Preconditions:**
- [SPEC-160](../(SPEC-160)-Chart-Critical-Path-Lens/(SPEC-160)-Chart-Critical-Path-Lens.md) (critical path lens) must be implemented — this spec consumes its float and critical path data
- Graph cache must be built

**Postconditions:**
- No changes to artifacts — scoring is computed at query time, not persisted in frontmatter
- Existing `priority-weight` semantics are preserved — the computed score augments, not replaces

## Acceptance Criteria

- **AC1**: Given two ready artifacts with the same `priority-weight` where one is on the critical path and the other is not, when `chart.sh recommend` is run, then the critical-path artifact ranks higher.
- **AC2**: Given two ready artifacts both on the critical path where one has `priority-weight: high` and the other `priority-weight: low`, when run, then the high-weight artifact ranks higher (operator intent is respected).
- **AC3**: Given an artifact blocking 5 downstream artifacts and another blocking 0, all else equal, when run, then the blocking artifact ranks higher.
- **AC4**: Given `--explain SPEC-NNN`, when run, then output shows the numeric score and its component breakdown (weight contribution, critical path contribution, float contribution, blocked count contribution).
- **AC5**: Given a custom `.agents/priority-weights.yaml` with modified `W_CRITICAL: 0`, when run, then critical path membership has no effect on scoring (weight constants are configurable).
- **AC6**: Given `--json`, when run, then output includes `urgency_score` (float) and `score_components` (object with named factors) per artifact.
- **AC7**: Given the existing `chart.sh recommend` output format, when run without `--json` or `--explain`, then the output is backward-compatible with an additional `score` column.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- **Augments, not replaces** — `priority-weight` remains the operator's explicit signal. Computed score layers structural data on top.
- **Query-time computation** — scores are not persisted. Every `recommend` invocation recomputes from current graph state.
- **Depends on SPEC-160** — critical path and float data must be available. If SPEC-160 is not yet implemented, `chart.sh recommend` falls back to current behavior (weight-only sorting) with a warning.
- **Not in scope**: task-level priority scoring within tk plans. Not in scope: age-based urgency decay (could be a future factor). Not in scope: due-date awareness (swain has no due dates).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-23 | — | Created from [SPIKE-042](../../../research/Active/(SPIKE-042)-Critical-Path-Analysis-For-Swain/(SPIKE-042)-Critical-Path-Analysis-For-Swain.md) findings; depends on [SPEC-160](../(SPEC-160)-Chart-Critical-Path-Lens/(SPEC-160)-Chart-Critical-Path-Lens.md) |
