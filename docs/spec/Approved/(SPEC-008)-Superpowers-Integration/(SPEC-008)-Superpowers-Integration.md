---
title: "Superpowers Integration"
artifact: SPEC-008
status: Approved
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
type: feature
parent-epic: EPIC-004
linked-research:
  - SPIKE-004
linked-adrs:
  - ADR-001
depends-on: []
addresses: []
evidence-pool:
source-issue:
swain-do: required
---

# SPEC-008: Superpowers Integration

## Problem Statement

Swain and obra/superpowers (v5.0.1) have complementary strengths but overlap in spec authoring, implementation planning, and completion verification. ADR-001 chose coexistence via a three-layer model. This spec defines the concrete integration points that enable both systems to operate together without conflicts.

## External Behavior

Nine integration points, each modifying swain skill behavior when superpowers is detected:

1. **Brainstorming routing** — swain-design checks for superpowers' brainstorming skill at artifact creation. If present, routes Visions and Personas through Socratic brainstorming flow. Other artifact types (Stories, Spikes, ADRs, Bugs, Runbooks, Designs, Journeys) use standard swain templates. Detection: presence check of superpowers skill directory.

2. **Thin SPEC format** — SPEC template drops the Implementation Approach section when superpowers is present. SPECs become thin contracts: acceptance criteria, scope, dependencies, ADR links, verification gate. Superpowers' writing-plans generates the detailed execution plan from acceptance criteria at implementation time.

3. **Task tracking mediation** — swain-do intercepts superpowers plan output. When writing-plans produces a plan file (`docs/plans/YYYY-MM-DD-*.md`), swain-do's `ingest-plan.py` script parses `### Task N:` blocks and creates bd items with spec lineage labels. TodoWrite is not used.

4. **Execution preference** — When superpowers is installed, subagent-driven development is the preferred execution strategy. swain-do's bd-tracked serial execution is the fallback for environments without superpowers or for tasks too simple for subagent overhead.

5. **TDD adoption** — Adopt superpowers' strict RED-GREEN-REFACTOR enforcement with anti-rationalization tables in swain-do's implementation methodology. This is a swain skill enhancement — the TDD discipline gets baked into swain-do regardless of whether superpowers is installed at runtime.

6. **Worktree integration** — Use superpowers' git worktree skill when implementing specs. swain-do tracks the branch-to-artifact relationship (which worktree implements which SPEC).

7. **Code review gate** — Use superpowers' code review skills (requesting + receiving) as part of the Testing → Implemented transition. The spec compliance reviewer checks against acceptance criteria; the code quality reviewer checks implementation.

8. **Session preflight** — Replace swain-doctor's auto-invoke with a lightweight shell script (`swain-preflight.sh`). Exit 0 = skip doctor, proceed to superpowers bootstrap → swain-session. Exit 1 = invoke full doctor. Checks: governance files exist, gitignore sane, no known broken state.

9. **Completion verification** — Adopt superpowers' verification-before-completion pattern universally. "No completion claims without fresh verification evidence" becomes a rule in swain-do for any task, not just SPEC acceptance criteria.

## Acceptance Criteria

1. **Given** superpowers' brainstorming skill is present, **when** creating a Vision artifact, **then** swain-design routes through Socratic brainstorming flow before capturing into swain's artifact format
2. **Given** superpowers' brainstorming skill is present, **when** creating a Story or Spike, **then** swain-design uses standard template (no brainstorming routing)
3. **Given** superpowers is present, **when** a SPEC is created, **then** the SPEC omits the Implementation Approach section
4. **Given** a superpowers plan file exists, **when** implementation begins, **then** `ingest-plan.py` creates bd tasks with `spec:<ID>` labels and sequential dependencies
5. **Given** superpowers is installed, **when** implementation tasks are dispatched, **then** subagent-driven development is used (with bd serial as fallback)
6. **Given** swain-do creates an implementation plan, **then** it includes anti-rationalization tables for TDD enforcement
7. **Given** a spec is being implemented, **when** superpowers worktree skill is available, **then** swain-do records the worktree branch ↔ artifact mapping
8. **Given** a SPEC transitions Testing → Implemented, **when** superpowers review skills are available, **then** both spec compliance and code quality reviews are requested
9. **Given** any session starts, **when** `swain-preflight.sh` exits 0, **then** swain-doctor is skipped and superpowers bootstrap proceeds directly
10. **Given** any task is claimed as complete, **then** fresh verification evidence must be provided (not just SPEC acceptance criteria — any task)

## Verification

<!-- Populated when entering Testing phase -->

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Superpowers detection mechanism (skill directory presence check)
- Routing rules for brainstorming by artifact type
- SPEC template conditional sections
- Plan ingestion script enhancements
- swain-do TDD methodology updates
- Preflight script design and implementation
- Completion verification broadening

**Out of scope:**
- Multi-platform support (swain remains Claude Code only)
- Contributing upstream to superpowers
- Replacing superpowers' internal skill format
- Building superpowers skills from scratch (we adopt, not rebuild)

**Constraints:**
- Superpowers evolves independently — integration must be loose coupling, not tight binding
- All integration is optional — swain must function fully without superpowers installed
- No TodoWrite usage — bd is the single task tracking backend

## Implementation Approach

Nine integration points, implementable independently:

**Phase 1 — Foundation (no superpowers runtime dependency):**
- TDD anti-rationalization tables in swain-do (standalone enhancement)
- Completion verification broadening in swain-do (standalone enhancement)
- Preflight script replacing doctor auto-invoke (standalone enhancement)

**Phase 2 — Detection and routing:**
- Superpowers presence detection utility
- Brainstorming routing in swain-design
- Conditional SPEC template sections

**Phase 3 — Execution integration (requires superpowers installed):**
- Plan ingestion via `ingest-plan.py`
- Subagent dispatch preference in swain-do
- Worktree ↔ artifact mapping
- Code review gate at Testing → Implemented

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Approved | 2026-03-12 | — | Skipped Draft/Review — developed through SPIKE-004 research and operator review |
