---
title: "Deduplicate Cross-Skill Boilerplate"
artifact: SPEC-017
status: Complete
type: enhancement
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic: EPIC-006
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
linked-artifacts:
  - SPIKE-010
  - SPIKE-011
depends-on-artifacts: []
---

# Deduplicate Cross-Skill Boilerplate

## Problem Statement

SPIKE-010 identified three duplication patterns across skills:

1. **Session bookmark boilerplate** (~546 tokens) — identical find+invoke+format blocks in 6 skills
2. **Four-tier tracking model** (~500 tokens) — same Implementation/Coordination/Research/Reference table in swain-design and swain-do
3. **Superpowers detection** (~1,363 tokens) — same `ls .claude/skills/.../SKILL.md` pattern in 3 skills

## External Behavior

Each duplicated pattern is reduced to a one-line directive or a shared reference. No behavior changes.

### Deduplication approach

**Session bookmark (6 copies → 1 directive):**
Replace the multi-line find+invoke+format block in each skill with:
```
After state-changing operations, update the session bookmark: `bash "$BOOKMARK" "<note>" --files <paths>`
```
The `BOOKMARK` variable and script location pattern move to AGENTS.md or a shared reference.

**Tracking tiers (2 copies → 1 reference):**
Keep the canonical table in swain-do (which owns execution tracking). swain-design references it: "See swain-do SKILL.md § Artifact handoff protocol for the four-tier tracking model."

**Superpowers detection (3 copies → 1 shared helper):**
Move detection logic to a shared script or reference file. Each skill reads the cached result.

## Acceptance Criteria

- **Given** session bookmark instructions, **when** counted across all SKILL.md files, **then** ≤1 full block exists (others are one-line directives)
- **Given** tracking tier table, **when** counted, **then** ≤1 full copy exists
- **Given** superpowers detection, **when** counted, **then** ≤1 full detection block exists
- **Given** any deduplicated directive, **when** the agent executes the workflow, **then** it finds and uses the canonical source correctly

## Scope & Constraints

- Can run in parallel with SPEC-015 and SPEC-016
- Changes touch multiple SKILL.md files — coordinate with other EPIC-006 specs
- AGENTS.md may gain a small shared section for cross-cutting patterns

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | — | Initial creation from EPIC-006 decomposition |
| Implemented | 2026-03-13 | 5d66e53 | All three deduplication criteria pass |
