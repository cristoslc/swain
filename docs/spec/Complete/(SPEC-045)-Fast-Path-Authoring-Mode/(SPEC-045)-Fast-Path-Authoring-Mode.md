---
title: "Fast-Path Authoring Mode for Low-Complexity Artifacts"
artifact: SPEC-045
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-014
linked-artifacts:
  - EPIC-014
depends-on-artifacts:
  - SPIKE-018
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Fast-Path Authoring Mode for Low-Complexity Artifacts

## Problem Statement

The swain-design authoring ceremony is uniform regardless of artifact complexity. Bug SPECs and trivial enhancement notes bear the same cost as feature SPECs and EPICs: specwatch scan, specgraph scope, ADR compliance check, and a two-commit lifecycle stamp — totaling ~8000 tokens and ~12 tool calls. For low-complexity artifacts, this overhead exceeds the artifact's value and discourages filing.

SPIKE-018 established the fast-path definition: skip specwatch scan, specgraph scope, hash-stamp commit, and index update for artifacts matching the "low complexity" tier.

## External Behavior

### Complexity tier detection

When swain-design creates an artifact, it applies the following tier detection heuristic before executing the authoring ceremony:

**Low complexity (fast-path eligible)**:
- `type: bug` or `type: fix` SPEC with no `parent-epic` and no downstream `depends-on` links
- SPIKE with no parent epic
- Any SPEC explicitly requested with a `--fast` flag or natural language equivalent ("quick", "simple", "trivial")

**Medium/High complexity (full ceremony)**:
- Feature SPECs
- SPECs with a `parent-epic`
- EPICs, Visions, Journeys, ADRs
- Any artifact where the user describes significant architectural decisions

### Fast-path ceremony (low complexity)

Steps **skipped** in fast-path mode:
1. `specwatch.sh scan` — skipped; relies on pre-session scan being clean
2. `specgraph.sh scope` — skipped; no vision alignment check for trivial artifacts
3. Index update (`list-*.md`) — deferred; updated lazily on next cache build
4. Hash-stamp commit — folded inline into the transition commit (see SPEC-046)

Steps **always kept**:
1. Number scan (find next available artifact ID)
2. Template read and artifact write
3. `adr-check.sh` run (retained — 73ms, catches real compliance issues)
4. Git commit for the artifact creation/transition

### Operator feedback

When fast-path is applied, swain-design outputs a single indicator line:
```
[fast-path] Skipped: specwatch scan, scope check, index update
```

No prompt or confirmation required — the tier detection is automatic.

## Acceptance Criteria

1. **Given** a bug SPEC with no parent epic, **when** swain-design creates it, **then** specwatch scan, specgraph scope, and index update are skipped; adr-check still runs.
2. **Given** a feature SPEC with a parent epic, **when** swain-design creates it, **then** the full ceremony runs (no fast-path).
3. **Given** an artifact created with explicit "quick" or "trivial" language, **when** swain-design creates it, **then** fast-path is applied.
4. **Given** fast-path is applied, **when** the artifact is created, **then** a `[fast-path]` indicator line appears in the output.
5. **Given** fast-path is applied, **when** adr-check runs, **then** any RELEVANT or DEAD_REF findings are still surfaced.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| | | |

## Scope & Constraints

- Fast-path applies to the authoring step only — lifecycle transitions (Ready→Active→Complete) use the same rules
- The `adr-check.sh` step is never skipped — it's 73ms and catches real issues
- If specwatch scan was NOT clean in the current session, downgrade to full ceremony even for low-complexity artifacts

## Implementation Approach

1. Add a `_complexity_tier()` heuristic function to the swain-design skill that classifies artifacts based on type, parent-epic, and explicit signals.
2. Add conditional skipping of specwatch, specgraph scope, and index update when tier is "low".
3. Output the `[fast-path]` indicator line when fast-path applies.
4. Update the swain-design skill documentation to describe the two tiers.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | c0e77ed2b6f273cb273a6e9c011149c13831c18c | Initial creation from EPIC-014 decomposition; SPIKE-018 findings confirmed GO |
| Ready | 2026-03-14 | c0e77ed | Approved — SPIKE-018 findings reviewed, GO confirmed |
| Complete | 2026-03-14 | b4892cd | Fast-path tier detection and lazy index rebuild.sh implemented; swain-design SKILL.md updated |
