---
title: "Swain"
artifact: VISION-001
track: standing
status: Superseded
superseded-by: PURPOSE.md
product-type: personal
author: cristos
created: 2026-03-11
last-updated: 2026-03-24
trove: ""
linked-artifacts:
  - PERSONA-001
  - PERSONA-002
  - SPIKE-003
  - VISION-003
  - VISION-004
  - SPEC-164

depends-on-artifacts: []
---

# Swain

## Target Audience

- **The operator** (PERSONA-001) — a solo developer who works with AI coding agents. Makes decisions; delegates implementation.
- **The agent** (PERSONA-002) — any AI coding agent. Stateless across sessions, needs structured context to execute correctly. A black box to swain.

## Value Proposition

Swain is a decision-support and implementation-alignment system for solo developers who work with AI coding agents.

**For the operator**, swain captures intent, structures it into reviewable artifacts, surfaces what needs a decision, and preserves the *why* behind choices — decision history that can't be derived from the codebase alone. Once a decision is made, swain protects it: downstream work is automatically checked against the decision's criteria, and violations are surfaced without re-prompting the operator for alignment they've already given.

**For the agent**, swain provides alignment — acceptance criteria, scope boundaries, constraints, and dependency graphs — then verifies outcomes against those criteria. How the agent works internally is irrelevant; any agent that reads markdown can participate.

Three questions drive the entire system:

1. **"What needs a decision?"** — the operator's question.
2. **"What's ready for implementation?"** — the agent's question.
3. **"Are my past decisions still holding?"** — the system's question.

## Problem Statement

AI coding agents are fast but stateless. Without a structured system of record, decisions pile up, agents implement against stale intent, and the reasoning behind past choices is lost. Without decision protection, the system that was supposed to support decisions becomes a decision tax — the operator gets re-asked the same alignment questions on every derived spec, every implementation task, every session. The gap isn't code quality — it's the coordination layer between human decisions and agent execution.

## Success Metrics

- The operator can answer "what needs my decision?" in under 30 seconds
- A fresh agent session can find the next implementable work item without conversational back-and-forth
- Decision history is preserved and discoverable — not just what was built, but what was considered and why
- Artifact state is the single source of truth
- Swapping agent runtimes requires zero changes to swain

## Non-Goals

- Not a team tool — solo operator + agent(s) only
- Not an agent runtime — alignment and verification, not execution
- Not a replacement for git — git is the persistence layer
- Not prescriptive about agent choice

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-11 | 7aadee8 | Initial creation from SPIKE-003 philosophical reframe |
| Active | 2026-03-11 | b9d0f65 | Transition to Active |
| Superseded | 2026-03-24 | c088911 | Superseded by PURPOSE.md — identity content migrated to project-root document outside artifact governance |
