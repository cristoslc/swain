---
title: "Evidence Basis For All Actions"
artifact: SPEC-117
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-005
linked-artifacts:
  - ADR-011
  - SPEC-114
  - SPIKE-022
  - ADR-005
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Evidence Basis For All Actions

## Problem Statement

During the SPIKE-022 session, the agent repeatedly reached conclusions before verifying premises, then built on those unverified conclusions. Each layer of analysis inherited prior errors. The operator's corrections were all variants of "can you prove that?" swain-search already enforces a "sources before synthesis" principle for formal research (troves), but this discipline is not applied to other agent activities: implementation plans, releases, phase transitions, root cause analysis, ADR drafting, or completion claims.

## External Behavior

**Before:** Agent performs actions (plans, transitions, releases, analysis) based on reasoning alone. Evidence is implicit — the agent read something and concluded something, but the evidence basis is not visible to the operator and not persisted for later review.

**After:** Every swain action has a visible, persisted evidence basis. Before any synthesis step (analysis, proposal, plan, claim), the agent:

1. Assembles an evidence index — a list of pointers into git:
   - Artifact ID + commit hash (e.g., `ADR-005 @ aa9ca7b`)
   - Source file + blob hash (e.g., `skills/swain-sync/SKILL.md @ d259c45`)
   - Retro quotes, test output references, git log entries
2. Presents the evidence index to the operator (inline in the conversation)
3. Persists it via `tk add-note` on the active task AND a session-level evidence log

The git history provides the backing store — the index contains pointers, not copies. If a claim can't be grounded in an observable source, the agent states "I don't know" or "this is speculation" rather than asserting it as fact.

## Acceptance Criteria

### AC1: Evidence index format defined

**Given** the need for a lightweight, machine-parseable evidence format
**When** the spec is implemented
**Then** a documented format exists for evidence indexes (artifact refs, file+blob refs, git log refs) that can be embedded in tk notes and session logs

### AC2: swain-do emits evidence on plan creation

**Given** an agent is creating an implementation plan for a SPEC
**When** the plan is created
**Then** a `tk add-note` on the plan epic contains the evidence index showing what artifacts and files were read to produce the plan

### AC3: swain-design emits evidence on artifact creation/transition

**Given** an agent is creating or transitioning an artifact
**When** the operation completes
**Then** the commit message or a tk note contains the evidence index showing what was read

### AC4: swain-release emits evidence on release

**Given** an operator invokes swain-release
**When** the release is proposed
**Then** the evidence basis (tag history, commit log, version files found) is presented visibly before the operator confirms

### AC5: Session evidence log persisted

**Given** a session produces multiple actions with evidence bases
**When** the session ends or sync occurs
**Then** a session-level evidence log is persisted (format and location TBD — could be a file in `.agents/`, a tk note on a session task, or appended to session.json)

### AC6: Ungrounded claims flagged

**Given** the agent cannot point to observable evidence for a claim
**When** it would otherwise state the claim as fact
**Then** it qualifies the claim with "speculation", "unverified", or "I don't know" rather than asserting it

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Define the evidence index format
- Add evidence emission to swain-do (plan creation, task completion)
- Add evidence emission to swain-design (artifact creation, transitions)
- Add evidence emission to swain-release (release proposal)
- Define session evidence log format and persistence mechanism
- Update AGENTS.md with the "evidence before conclusions" governance rule

**Out of scope:**
- Automated verification that evidence was collected (behavioral guidance, not enforcement)
- Changes to swain-search (already has this discipline via troves)
- Retroactive evidence collection for past actions

**Constraints:**
- The evidence index must be cheap to produce — pointers only, no content duplication
- Must not add significant latency to agent operations
- Must work in both interactive and dispatched (background) agent contexts

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | ec9842d | From SPIKE-022-to-SPEC-114 retro |
