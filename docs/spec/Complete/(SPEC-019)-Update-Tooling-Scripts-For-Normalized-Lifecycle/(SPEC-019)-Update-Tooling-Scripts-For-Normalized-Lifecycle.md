---
title: "Update Tooling Scripts for Normalized Lifecycle"
artifact: SPEC-019
track: implementable
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-008
linked-artifacts:
  - ADR-003
depends-on-artifacts:
  - SPEC-018
implementation-commits:
  - 8991172
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Update Tooling Scripts for Normalized Lifecycle

## Problem Statement

specgraph.sh, specwatch.sh, swain-status.sh, and spec-verify.sh all hard-code per-type lifecycle phase names. After ADR-003's three-track normalization, these scripts must recognize the new phase vocabulary and organize output by track rather than individual type.

## External Behavior

### specgraph.sh

- Phase-based status detection uses new phase names (Proposed, Ready, In Progress, Needs Manual Test, Complete, Active, Retired, Superseded, Abandoned)
- `status` subcommand groups by track (Implementable, Container, Standing) rather than individual type
- Ready/blocked resolution uses the new phases
- `mermaid` output reflects new lifecycle arrows

### specwatch.sh

- Stale reference detection uses new phase subdirectory names
- Phase validation checks against the three-track model (not per-type ad-hoc lists)
- STORY references flagged as stale (type removed)

### swain-status.sh

- Phase labels in output use new names
- Epic progress calculation uses new terminal phase names (Complete instead of Implemented)

### spec-verify.sh

- Testing phase check updated: "Needs Manual Test" replaces "Testing"
- Implemented check updated: "Complete" replaces "Implemented"

### SKILL.md references

- swain-design SKILL.md phase transition docs reference new phases
- swain-do SKILL.md references to SPEC lifecycle updated
- swain-status SKILL.md updated

## Acceptance Criteria

- **Given** an artifact with status "Proposed", **when** specgraph runs, **then** it correctly identifies the artifact as unresolved/actionable
- **Given** a SPEC with status "Complete", **when** specgraph runs, **then** it counts as resolved (not "Implemented")
- **Given** an artifact referencing a removed STORY, **when** specwatch runs, **then** it flags the reference as stale
- **Given** a SPEC in "Needs Manual Test", **when** spec-verify.sh runs, **then** it validates the verification table
- **Given** swain-status runs, **when** epics show progress, **then** child SPECs use "Complete" as the done state

## Scope & Constraints

- Only changes script logic and SKILL.md docs — not artifact files themselves
- Depends on SPEC-018 (definitions must be final before scripts encode them)
- Does NOT migrate existing artifacts (SPEC-020)

## Implementation Approach

1. Update specgraph.sh phase detection arrays and status comparisons
2. Update specwatch.sh phase validation and directory scanning
3. Update swain-status.sh phase labels
4. Update spec-verify.sh phase checks
5. Update SKILL.md files for swain-design, swain-do, swain-status
6. Test each script against the updated definitions

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 232369c | Initial creation |
| Complete | 2026-03-13 | c2859a2 | Implementation verified |
