---
title: "Inline Lifecycle Hash Stamping for Trivial Artifacts"
artifact: SPEC-046
track: implementable
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-014
linked-artifacts:
  - EPIC-014
depends-on-artifacts:
  - SPIKE-018
  - SPEC-045
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Inline Lifecycle Hash Stamping for Trivial Artifacts

## Problem Statement

The two-commit lifecycle stamp pattern (one commit for the transition, one commit to back-fill the hash into the lifecycle table) was designed for correctness: it produces a verifiable hash that documents the exact commit hash in the lifecycle row. But it adds ~2500 tokens and a full agent-commit round-trip per artifact — accounting for ~31% of the total authoring ceremony cost (per SPIKE-018).

For trivial artifacts (bug SPECs, research notes), the stamp has low value: nothing downstream links to these artifacts, and the lifecycle table is rarely consulted for auditing. The overhead is disproportionate.

## External Behavior

### Inline stamp mode

For artifacts eligible for fast-path mode (per SPEC-045), the lifecycle transition commit includes the hash inline instead of requiring a second commit:

**Before (two-commit pattern)**:
```
Commit A: lifecycle(SPEC-099): transition to Complete
  ↳ lifecycle table row: | Complete | 2026-03-14 | -- | ... |

Commit B: docs(SPEC-099): stamp lifecycle hash for Complete transition
  ↳ lifecycle table row: | Complete | 2026-03-14 | <commit-A-hash> | ... |
```

**After (inline stamp pattern)**:
```
Commit A: lifecycle(SPEC-099): transition to Complete
  ↳ lifecycle table row: | Complete | 2026-03-14 | <HEAD-1 hash> | ... |
```

The inline stamp uses the *previous* HEAD hash (the implementation commit) rather than the transition commit hash. This is slightly less precise but eliminates the second commit entirely.

### When inline stamp applies

Inline stamp applies when:
- The artifact is in fast-path tier (per SPEC-045 classification)
- The artifact has no downstream artifacts linking to it via `depends-on` or `linked-artifacts`

Full two-commit stamp remains for:
- EPICs (always — they are linked by child SPECs)
- SPECs with downstream dependents
- Any artifact where the operator explicitly requests a stamp commit

### Operator feedback

No change to visible output — the lifecycle table just has the hash pre-filled.

## Acceptance Criteria

1. **Given** a low-complexity SPEC with no downstream dependents, **when** it transitions to Complete, **then** the lifecycle row has the implementation commit hash pre-filled (no `--` placeholder).
2. **Given** a low-complexity SPEC, **when** the transition commit is created, **then** only one commit is made (no second stamp commit).
3. **Given** an EPIC or a SPEC with downstream dependents, **when** it transitions to Complete, **then** the two-commit pattern is preserved.
4. **Given** an artifact with an inline stamp, **when** specgraph or swain-status reads the lifecycle table, **then** the hash is valid and resolves to an existing commit.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- The inline stamp uses `git rev-parse HEAD` *before* the transition commit, giving the implementation commit hash
- This creates a ~1-commit offset (lifecycle row points to implementation, not transition) — acceptable for trivial artifacts
- High-value artifacts (EPICs, feature SPECs with children) continue to use the two-commit pattern

## Implementation Approach

1. In the artifact transition workflow, check if the artifact is fast-path eligible and has no downstream dependents.
2. If so, compute `git rev-parse HEAD` before the transition commit and pre-fill the lifecycle row hash.
3. Skip the second stamp commit entirely.
4. Update swain-design documentation to describe when inline vs. two-commit stamping applies.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | -- | Initial creation from EPIC-014 decomposition; follows SPEC-045 fast-path classification |
