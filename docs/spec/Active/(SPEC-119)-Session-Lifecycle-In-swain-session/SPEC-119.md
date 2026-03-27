---
title: "Session Lifecycle in swain-session"
artifact: SPEC-119
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
  - SPEC-170
  - SPEC-121
  - SPEC-123
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Session Lifecycle in swain-session

## Problem Statement

swain-session currently manages tab names and bookmarks but has no concept of a bounded work session with start, work, and close phases.

## External Behavior

**Before:** swain-session sets terminal tab names and writes a bookmark file. There is no session lifecycle, no decision budget, no structured start/close.

**After:** swain-session is rebuilt from the ground up to own the session lifecycle:

- **Start**: propose focus lane (default to previous; operator confirms or redirects), generate SESSION-ROADMAP.md, set decision budget (default 3-5, configurable)
- **Work**: as decisions are made via other skills, SESSION-ROADMAP.md accumulates decision records
- **Close**: finalize SESSION-ROADMAP.md with progress summary and walk-away signal, commit to git
- **Resume**: on next session start, read previous SESSION-ROADMAP.md from git, surface what changed in the interim (new issues, completed background work, external signals)

Session state is persisted in a lightweight file (`.agents/session-state.json` or similar) containing: session ID, start time, focus lane, decision budget, decisions made count.

## Acceptance Criteria

### AC1: Session start proposes focus lane

**Given** the operator invokes swain-session start
**When** the skill runs
**Then** it proposes a focus lane (defaulting to previous session's lane) and waits for operator confirmation

### AC2: Session start generates SESSION-ROADMAP.md

**Given** the operator confirms a focus lane
**When** session start completes
**Then** SESSION-ROADMAP.md is generated via chart.sh session

### AC3: Session close commits SESSION-ROADMAP.md

**Given** the operator invokes swain-session close
**When** the skill runs
**Then** SESSION-ROADMAP.md is finalized with a walk-away signal and committed to git

### AC4: Session state persists across context clears

**Given** an active session
**When** the terminal context is cleared and a new conversation starts
**Then** session state is recoverable from `.agents/session-state.json`

### AC5: Resume surfaces interim changes

**Given** a previous session was closed
**When** the operator starts a new session
**Then** changes since last close (new issues, completed background work) are surfaced

### AC6: Decision budget is configurable

**Given** the operator starts a session
**When** they specify a custom decision budget (e.g., `--budget 7`)
**Then** the session uses that budget instead of the default

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- Complete rebuild of swain-session skill
- Session lifecycle: start, work, close, resume
- Session state persistence via `.agents/session-state.json`
- Integration with chart.sh session (SPEC-118) for SESSION-ROADMAP.md generation
- Decision budget tracking

**Out of scope:**
- SESSION-ROADMAP.md format definition (SPEC-118)
- ROADMAP.md changes (SPEC-170)
- Session detection in other skills (SPEC-121)

**Constraints:**
- Session state file must be lightweight and human-readable (JSON)
- Resume must work even if the previous session was not cleanly closed
- Decision budget is a soft limit -- the operator can always override

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-20 | -- | Initial creation |
