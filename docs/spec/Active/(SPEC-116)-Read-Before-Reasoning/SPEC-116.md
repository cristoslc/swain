---
title: "Read Before Reasoning"
artifact: SPEC-116
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: enhancement
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - SPEC-114
  - SPIKE-022
  - ADR-005
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Read Before Reasoning

## Problem Statement

During the SPIKE-022 investigation, the agent built an elaborate TOCTOU analysis and three-layer mitigation strategy without reading ADR-005 — the existing worktree landing workflow. When the operator asked "why was cherry-pick being used?", reading ADR-005 immediately revealed the actual mechanism (rebase + push HEAD:main) and collapsed the analysis to "use merge instead of rebase." Hours of overengineering resulted from not loading relevant context before reasoning.

The pattern: the agent starts analyzing and proposing before reading the existing artifacts and their linked references. Each conclusion built on unread premises inherits errors from the gap.

## External Behavior

**Before:** Agent receives a problem or task, begins analysis immediately, reads artifacts only when specifically prompted or when a detail is needed.

**After:** Before any investigation, solution design, root cause analysis, or artifact creation, the agent follows a context-loading protocol:

1. Identify the immediate artifact(s) relevant to the work
2. Read them
3. Follow `linked-artifacts`, `depends-on-artifacts`, `parent-epic`, `parent-initiative`, and `parent-vision` references
4. Read those linked artifacts
5. Only then begin analysis or proposal

This protocol is encoded in the skill files that govern agent behavior (AGENTS.md, swain-design SKILL.md, swain-do SKILL.md) so it ships to all swain consumers.

## Acceptance Criteria

### AC1: AGENTS.md governance rule

**Given** AGENTS.md is the top-level behavioral governance file
**When** the spec is implemented
**Then** AGENTS.md contains a "Read before reasoning" rule requiring agents to load immediate + linked artifact context before analysis

### AC2: swain-design context loading

**Given** swain-design handles investigation, analysis, and artifact creation
**When** the skill is invoked for any operation that references existing artifacts
**Then** the SKILL.md contains a step requiring the agent to read the artifact and follow its linked references before proposing changes

### AC3: swain-do context loading

**Given** swain-do handles implementation planning and task execution
**When** a SPEC comes up for implementation
**Then** the SKILL.md contains a step requiring the agent to read the SPEC, its parent artifacts, and any linked ADRs/SPIKEs before creating a plan

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Add governance rule to AGENTS.md
- Add context-loading steps to swain-design SKILL.md
- Add context-loading steps to swain-do SKILL.md
- Update any other skill files that perform analysis or investigation (swain-retro, swain-sync worktree detection)

**Out of scope:**
- Automated enforcement (scripts that verify context was loaded) — behavioral guidance only
- Changes to swain-search (already has sources-before-synthesis)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | ec9842d | From SPIKE-022-to-SPEC-114 retro |
