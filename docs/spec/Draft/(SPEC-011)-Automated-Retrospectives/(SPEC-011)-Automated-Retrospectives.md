---
title: "Automated Retrospectives"
artifact: SPEC-011
status: Draft
type: feature
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
parent-epic:
linked-research: []
linked-adrs: []
depends-on: []
addresses: []
evidence-pool: ""
source-issue: "github:cristoslc/swain#20"
swain-do: required
---

# Automated Retrospectives

## Problem Statement

Agent work produces learnings — what went well, what surprised, what patterns to repeat or avoid — but these learnings evaporate between sessions. There's no structured mechanism to capture and surface them. The auto-memory system exists but isn't triggered systematically at natural reflection points.

## External Behavior

A new cross-cutting skill (`swain-retro`) that captures retrospective learnings at natural completion points and persists them for future use.

### Triggers

1. **EPIC completion** — when an EPIC transitions to Complete, swain-retro is automatically invoked
2. **Manual** — user invokes `/swain-retro` at any time

### Output

1. **Memory files** — a reflecting agent prompts the user with targeted questions about the completed work, then writes feedback-type and project-type memories based on the conversation
2. **Retro documents** — ongoing retro doc (and optional supporting files) stored in `docs/swain-retro/`. Each retro produces a dated markdown file capturing the full reflection, not just the distilled memories

### Reflection flow

1. Agent reviews what was done (git log, closed tasks, transitioned artifacts)
2. Agent prompts user with reflection questions (what went well, what was surprising, what would you change, what patterns emerged)
3. User responds conversationally
4. Agent distills into:
   - Memory files (feedback type for behavioral patterns, project type for context)
   - Retro doc in `docs/swain-retro/YYYY-MM-DD-<topic>.md` with the full reflection

### Scope

Cross-cutting — touches swain-do (EPIC completion hook), swain-design (artifact transition awareness), and swain-session (session context for reflection material).

## Acceptance Criteria

- **Given** an EPIC transitions to Complete, **when** the transition completes, **then** swain-retro is invoked automatically with the EPIC's context
- **Given** the user runs `/swain-retro`, **when** invoked manually, **then** the reflecting agent reviews recent work and prompts with reflection questions
- **Given** a retro conversation completes, **when** the agent distills learnings, **then** both memory files and a retro doc in `docs/swain-retro/` are produced
- **Given** retro docs exist from prior sessions, **when** a new retro runs, **then** the agent can reference patterns from previous retros

## Scope & Constraints

- The reflecting agent prompts the user — it does not auto-generate retro content without user input
- Memory files use the existing auto-memory system (feedback and project types)
- Retro docs are human-readable markdown, not structured data
- The EPIC completion hook is best-effort — if swain-retro isn't available, the transition still succeeds

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | 1170623 | Initial creation from GitHub #20 decision |
