---
title: "Integration Hooks and Decision Protection"
artifact: SPEC-097
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: ""
parent-epic: EPIC-035
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-094
  - SPEC-095
  - SPEC-096
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Integration Hooks and Decision Protection

## Problem Statement

The staleness detection script (SPEC-096) and schema changes (SPEC-094) need to be wired into swain's existing workflows. Additionally, the decision protection model — where alignment decisions cascade from Epic to child SPECs — needs to be implemented as an agent-level workflow in swain-design.

## External Behavior

### Automated hooks (script-level)

**specwatch scan:** Add `design-check.sh` call parallel to existing `train-check.sh` integration block (~10 lines mirroring the train-check pattern in specwatch.sh).

**swain-sync pipeline:** Add `design-check.sh` alongside Step 3.7 (ADR compliance check). Advisory, not blocking — report drift but don't fail the sync.

**DESIGN lifecycle hooks in swain-design:**
- Creation: validate all `sourcecode-refs` paths exist at HEAD
- Proposed → Active: validate all refs are CURRENT (existence + blob match)
- Active → Superseded: new DESIGN inherits `sourcecode-refs` from old one (with fresh pins)

### Agent-level hooks (judgment)

**SPEC Implementation transition:** When a SPEC transitions to Implementation and has a linked DESIGN (via either side's `linked-artifacts` or `artifact-refs`), surface the DESIGN's Intent section (Goals, Constraints, Non-goals) for alignment awareness.

**SPEC completion:** Cross-reference changed files (from `git diff`) against active DESIGNs' `sourcecode-refs`. If overlap found, nudge: "SPEC-NNN modified files tracked by DESIGN-NNN. Update the design to reflect changes?"

**Decision protection — alignment cascading:**
- When an operator confirms alignment between an Epic and a DESIGN (via `rel: [aligned]` on Epic's `artifact-refs`), record that decision.
- When a SPEC is derived under an aligned Epic, check SPEC scope/acceptance criteria against the DESIGN's Goals, Constraints, and Non-goals.
- Traversal path: SPEC → parent EPIC → `artifact-refs` with `rel: [aligned]` → DESIGN → Design Intent.
- Only surface violations — silent pass for aligned SPECs.

**Design→code drift direction:** When a DESIGN's mutable sections are modified but its `sourcecode-refs` blobs haven't changed, surface: "DESIGN-NNN evolved but tracked code hasn't caught up."

## Acceptance Criteria

- **Given** specwatch scan runs, **When** active DESIGNs have `sourcecode-refs`, **Then** `design-check.sh` is called and results included in scan output
- **Given** swain-sync runs, **When** active DESIGNs have stale `sourcecode-refs`, **Then** drift is reported as advisory (sync does not fail)
- **Given** a DESIGN transitions Proposed → Active, **When** `sourcecode-refs` entries exist, **Then** all paths are validated and blob SHAs match
- **Given** a SPEC transitions to Implementation with a linked DESIGN, **When** the transition fires, **Then** the DESIGN's Intent section is surfaced
- **Given** a SPEC completes and modified files overlap with a DESIGN's `sourcecode-refs`, **When** the completion hook fires, **Then** the operator is nudged to update the DESIGN
- **Given** an Epic has `artifact-refs` with `rel: [aligned]` pointing to a DESIGN, **When** a child SPEC is created, **Then** the SPEC's scope is checked against the DESIGN's Constraints and Non-goals
- **Given** a child SPEC's acceptance criteria conflict with a DESIGN constraint, **When** the integrity check runs, **Then** a specific violation is surfaced (not a generic "please review")
- **Given** a DESIGN's `last-updated` is newer than its `sourcecode-refs` `verified` dates, **When** detected, **Then** surface design→code drift direction

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- specwatch and swain-sync modifications are script-level (bash)
- Decision protection alignment check is agent-level (swain-design SKILL.md workflow step)
- The alignment integrity check compares structured text (SPEC acceptance criteria vs DESIGN constraints) — it is an agent judgment call, not a regex match
- Does not modify the specgraph query engine — uses existing traversal

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Created from EPIC-035 decomposition |
