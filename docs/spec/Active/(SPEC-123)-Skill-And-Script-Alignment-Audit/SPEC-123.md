---
title: "Skill and Script Alignment Audit"
artifact: SPEC-123
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-039
parent-initiative: INITIATIVE-019
linked-artifacts: []
depends-on-artifacts:
  - SPEC-118
  - SPEC-119
  - SPEC-120
  - SPEC-121
  - SPEC-122
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Skill and Script Alignment Audit

## Problem Statement

The session lifecycle rebuild changes fundamental assumptions across swain. Every skill, script, and reference document needs to be checked for alignment with the new session model. References to swain-status need updating. Session-unaware behaviors need session detection hooks. Documentation needs to reflect the two-document model (ROADMAP.md + SESSION-ROADMAP.md).

## External Behavior

**Before:** Skills and documentation reference swain-status, assume no session lifecycle, and have no awareness of SESSION-ROADMAP.md.

**After:** A systematic audit of all swain skills and scripts produces:

- Updated AGENTS.md reflecting session lifecycle and new routing
- Updated README.md with session workflow documentation
- Updated skill SKILL.md files with session detection hooks where applicable
- Updated reference docs that mention swain-status
- Updated swain router (swain meta-skill) routing table

This is the final spec -- it runs after all other specs in the epic are complete.

## Acceptance Criteria

### AC1: Every SKILL.md reviewed

**Given** all other EPIC-039 specs are complete
**When** the audit runs
**Then** every SKILL.md in the project has been reviewed for session alignment

### AC2: AGENTS.md updated

**Given** the session lifecycle is implemented
**When** the audit completes
**Then** AGENTS.md reflects the session lifecycle, routing, and two-document model

### AC3: README.md updated

**Given** the session workflow is new to users
**When** the audit completes
**Then** README.md documents the session workflow for new users

### AC4: No stale swain-status references

**Given** swain-status has been absorbed into swain-session
**When** all skill files are searched
**Then** no stale references to swain-status remain

### AC5: Router table updated

**Given** routing has changed
**When** the swain router table is inspected
**Then** it reflects the new session-based routing

### AC6: specwatch scan passes

**Given** all changes are complete
**When** specwatch scan runs
**Then** no warnings related to this epic's changes are reported

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Audit all SKILL.md files for session alignment
- Update AGENTS.md with session lifecycle
- Update README.md with session workflow
- Update all references to swain-status across all files
- Update swain router routing table
- Run specwatch scan to verify

**Out of scope:**
- Implementation of session features (covered by SPEC-118 through SPEC-122)
- New skill creation

**Constraints:**
- This spec must run last -- it depends on SPEC-118, SPEC-119, SPEC-120, SPEC-121, and SPEC-122
- Must be comprehensive -- every file in the project is in scope for review
- Changes must be backward-compatible where possible

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
