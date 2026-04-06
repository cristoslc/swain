---
title: "Raise FK Grade Threshold To 10"
artifact: SPEC-285
track: implementable
status: Active
author: operator
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-194
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Raise FK Grade Threshold To 10

## Problem Statement

The current Flesch-Kincaid grade-level threshold is set to 9. This is slightly too strict for technical documentation that often contains domain-specific terms. A threshold of 10 is more practical while still keeping prose accessible.

## Desired Outcomes

- Artifacts that score between 9 and 10 no longer trigger rewrites.
- Agent time spent on unnecessary readability revisions is reduced.
- All references to the threshold (governance, scripts, protocol docs) are consistent at grade 10.

## External Behavior

The default threshold changes from 9 to 10 in all locations:

| Location | Change |
|----------|--------|
| `readability-check.sh` | `THRESHOLD=9` becomes `THRESHOLD=10` |
| `AGENTS.content.md` (Readability section) | "grade level of 9" becomes "grade level of 10" |
| `AGENTS.md` (Readability section) | "grade level of 9" becomes "grade level of 10" |
| `readability-protocol.md` | "9th-grade" becomes "10th-grade" |
| `swain-design SKILL.md` (Readability section) | "9 or below" becomes "10 or below" |

The `--threshold` flag behavior is unchanged; only the default changes.

## Acceptance Criteria

1. **Given** `readability-check.sh` with no `--threshold` flag, **when** a file scores grade 9.5, **then** the result is PASS.

2. **Given** AGENTS.md and AGENTS.content.md, **when** an agent reads the readability rule, **then** it finds "grade level of 10."

3. **Given** readability-protocol.md, **when** a skill reads the protocol, **then** it references "10th-grade."

4. **Given** swain-design SKILL.md, **when** an agent reads the readability section, **then** it says "10 or below."

5. **Given** `readability-check.sh --threshold 8`, **when** a file scores grade 9, **then** the result is FAIL (custom threshold still works).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only the default threshold changes. The `--threshold` flag and all other behavior remain the same.
- Existing tests should still pass (the pass fixture scores well below 9, the fail fixture scores well above 10).
- [SPEC-194](../../Active/(SPEC-194)-Flesch-Kincaid-Readability-Enforcement/(SPEC-194)-Flesch-Kincaid-Readability-Enforcement.md) defined the original threshold; this spec updates it.

## Implementation Approach

Find-and-replace "9" with "10" in the five locations listed above. Run existing readability tests to confirm no regressions.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
