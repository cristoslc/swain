---
title: "Evidence Sidecars"
artifact: SPEC-272
track: implementable
status: Proposed
author: cristos
created: 2026-04-05
last-updated: 2026-04-05
priority-weight: ""
type: ""
parent-epic: EPIC-062
parent-initiative: ""
linked-artifacts:
  - DESIGN-019
depends-on-artifacts:
  - SPEC-271
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Evidence Sidecars

## Problem Statement

Test results live in JSON, but people read markdown. Today there is no per-scenario file that shows pass/fail, commit, and time. Parent artifacts have no local view of child evidence.

## Desired Outcomes

Each scenario gets a markdown sidecar with its latest result. Parents get symlinks to child sidecars so the full picture is clear at every level.

## External Behavior

- Sidecar path: `docs/spec/<Phase>/(SPEC-NNN)-Title/evidence/<scenario-id>.evidence.md`
- Built from `test-results.json` by tooling, not by agents
- Each sidecar holds: ID, title, test name, status, commit hash, time
- Parent Design/Epic evidence folders hold links to child sidecars
- swain-doctor fixes broken links (extends relink.sh)
- When the JSON file changes, sidecars are rebuilt (old ones replaced)

## Acceptance Criteria

**AC-1: One sidecar per scenario.**
Given a JSON file with three entries.
When the tool runs.
Then one file per entry appears in the spec's evidence/ folder.

**AC-2: Sidecar holds all fields.**
Given a sidecar built from one result.
When the user opens it.
Then it shows the ID, test name, status, commit, and time.

**AC-3: Parent links to child sidecars.**
Given a Design with two child specs that have sidecars.
When the tool runs.
Then the Design's evidence/ folder has links to each child file.

**AC-4: Null bdd_id means no sidecar.**
Given a result where bdd_id is null.
When the tool runs.
Then no sidecar is made for that entry.

**AC-5: Doctor fixes broken links.**
Given a link that points to a moved spec's sidecar.
When swain-doctor runs its relink pass.
Then the link target updates to the new path.

**AC-6: New results replace old sidecars.**
Given a sidecar from an older test run.
When new results arrive for the same entry.
Then the old sidecar is replaced with fresh data.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Sidecars are plain markdown — no structured data beyond what people can read
- Symlinks follow existing swain patterns (relink.sh, swain-doctor repair)
- Staleness stamps are SPEC-273's concern
- This spec does not decide when evidence is stale — only how to store and link it

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-05 | _pending_ | Decomposed from EPIC-062 |
