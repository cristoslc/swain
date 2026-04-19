---
title: "Retroactive Artifact Creation"
artifact: EPIC-086
track: container
status: Proposed
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
parent-vision: 004
parent-initiative: INITIATIVE-002
priority-weight: high
success-criteria:
  - Work built without prior documentation can be backfilled into the artifact graph with full rigor
  - Retroactive SPECs and EPICs are indistinguishable from prospective ones in the artifact graph
  - Git commit history is sufficient input to generate a retroactive spec with acceptance criteria and verification evidence
  - The operator can create retroactive artifacts from recent work without manual re-entry of information already captured in git
depends-on-artifacts:
  - PERSONA-004
addresses: []
evidence-pool: ""
---

# Retroactive Artifact Creation

## Goal / Objective

Allow the artifact graph to be backfilled for work that was already built without prior documentation. Shippers often code first and document after — currently the system has no way to capture that work retroactively. Every artifact must declare intent before execution, forcing a plan-first model on build-first practitioners. Retroactive creation produces valid artifact graph entries (indexes, lifecycle tables, frontmatter) from git history, giving the same traceability as prospective creation.

## Desired Outcomes

- **Shippers** can create a SPEC describing work they already built, placed directly in Complete with verification backfilled from test evidence.
- **Shippers** can create an EPIC grouping work that is already done, reconstructing the narrative from commit history.
- **Builders** reviewing the artifact graph see no distinction between prospective and retroactive entries — the same frontmatter, lifecycle, and verification quality.
- **The system** does not force a sequential plan-first model on practitioners who work differently.

## Progress

<!-- Auto-populated from session digests. -->

## Scope Boundaries

**In scope:**
- `swain-design create SPEC --retroactive` flag scanning git history and generating a SPEC in Complete
- `swain-design create EPIC --retroactive` flag grouping existing SPECs under a new epic
- Retroactive acceptance criteria derived from test evidence in the commit range
- Retroactive verification table populated from passing tests
- Lifecycle table recording the retroactive creation path

**Out of scope:**
- EXPERIMENT artifact type (isolated for SPIKE-069)
- CI/deployment hooks (folded into INITIATIVE-022 teardown)
- Changes to verification gate model (I22 owns this)
- Changes to lifecycle pathways or fast paths (EPIC-081 owns this)

## Child Specs

_To be decomposed when the epic transitions to Active._

## Key Dependencies

- Git history scanning requires structured commit messages (conventional commits) for accurate SPEC generation
- Test evidence extraction requires knowing which tests cover which acceptance criteria
- INITIATIVE-002 (Artifact System Maturity) is the natural home since retroactive creation is about filling gaps in the artifact graph

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-18 | — | Decomposed from EPIC-083 Abandoned |