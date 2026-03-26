---
title: "Refactor Skill Chaining Table Into Reference File"
artifact: SPEC-166
track: implementable
status: Proposed
author: cristos
created: 2026-03-24
last-updated: 2026-03-24
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPEC-164
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Refactor Skill Chaining Table Into Reference File

## Problem Statement

The superpowers skill chaining table in AGENTS.md governance is the heaviest section — 9 rows of dense routing rules that every agent parses on session start. For agents without superpowers installed, the entire table is irrelevant but must be read before reaching the escape hatch. The table mixes superpowers-only chains with always-active swain-to-swain chains, making it hard to scan.

This was identified during a governance template audit as part of [SPEC-164](../../Active/(SPEC-164)-PURPOSE-Migration-And-Vision-001-Supersession/(SPEC-164)-PURPOSE-Migration-And-Vision-001-Supersession.md).

## Desired Outcomes

The governance template is lighter and scannable. Agents without superpowers skip the detail immediately. The full routing table is preserved but lives in a reference file that skills consult when they need it.

## External Behavior

### Current
AGENTS.md contains the full 9-row chaining table inline.

### Proposed
AGENTS.md governance lists the skills that participate in chains and points to a reference file. The reference file contains the full routing table, the superpowers detection command, and the always-active vs. superpowers-only distinction.

## Acceptance Criteria

**AC-1:** The superpowers skill chaining section in AGENTS.content.md is replaced with a concise summary that lists participating skills and references the detail file.

**AC-2:** A reference file (e.g., `skills/swain-design/references/skill-chaining.md` or similar) contains the full routing table, separated into always-active chains and superpowers-only chains.

**AC-3:** All skills that currently reference the chaining table in AGENTS.md (swain-design SKILL.md, swain-do SKILL.md) are updated to reference the new location.

**AC-4:** AGENTS.md is regenerated from AGENTS.content.md and both are in sync.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The chaining rules themselves do not change — this is a structural refactor, not a behavioral change
- The reference file should be readable by both skills and agents
- AGENTS.md total token footprint should decrease measurably

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-24 | 3d696d0 | Agent-suggested during SPEC-164 governance audit |
