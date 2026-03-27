---
title: "Session Detection Hooks Across All Skills"
artifact: SPEC-121
track: implementable
status: Active
author: cristos
created: 2026-03-20
last-updated: 2026-03-20
type: feature
parent-epic: EPIC-039
parent-initiative: INITIATIVE-019
linked-artifacts:
  - SPEC-118
  - SPEC-169
  - SPEC-123
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Session Detection Hooks Across All Skills

## Problem Statement

Skills currently operate without awareness of whether the operator is in an active session. This means the operator can make unbounded decisions without the cognitive load management that the session lifecycle provides.

## External Behavior

**Before:** Skills execute without checking session state. The operator can invoke any skill at any time with no session context.

**After:** Every skill that performs state-changing operations checks for an active session before proceeding. If no session exists (or the current session is older than a configurable threshold, default 1 hour), the skill prompts the operator to start a new session. It does NOT auto-start -- the operator must explicitly confirm.

The check is a lightweight function call (read `.agents/session-state.json`, compare timestamp). Skills that are read-only (swain-help, swain-search in discover mode) skip the check.

## Acceptance Criteria

### AC1: State-changing skills check for active session

**Given** a state-changing skill is invoked (swain-design, swain-do, swain-release, etc.)
**When** no active session exists
**Then** the skill prompts the operator to start a new session before proceeding

### AC2: Stale session triggers prompt

**Given** a session exists but is older than the configurable threshold (default 1 hour)
**When** a state-changing skill is invoked
**Then** the skill treats the session as stale and prompts the operator

### AC3: Read-only skills skip the check

**Given** a read-only skill is invoked (swain-help, swain-search in discover mode)
**When** no active session exists
**Then** the skill proceeds without prompting

### AC4: Prompt is non-blocking

**Given** the session detection prompt appears
**When** the operator dismisses it
**Then** the skill proceeds without a session (no forced session creation)

### AC5: Performance constraint met

**Given** the session check runs on skill startup
**When** timed
**Then** it adds less than 100ms to skill startup time

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Session detection function (read `.agents/session-state.json`, compare timestamp)
- Integration into all state-changing skill SKILL.md files
- Configurable staleness threshold
- Skip list for read-only skills

**Out of scope:**
- Session lifecycle management (SPEC-169)
- SESSION-ROADMAP.md format (SPEC-118)
- Automatic session creation

**Constraints:**
- Session check must add < 100ms to skill startup
- Prompt must be non-blocking -- operator can always dismiss
- Must not break skills when `.agents/session-state.json` does not exist

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
