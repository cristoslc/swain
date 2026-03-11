---
title: "Swain"
artifact: VISION-001
status: Active
product-type: personal
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
depends-on: []
evidence-pool: ""
---

# Swain

## Target Audience

- **The operator** (PERSONA-001) — a solo developer who works with AI coding agents. Makes decisions; delegates implementation.
- **The agent** (PERSONA-002) — any AI coding agent. Stateless across sessions, needs structured context to execute correctly. A black box to swain.

## Value Proposition

Swain is a decision-support and implementation-alignment system for solo developers who work with AI coding agents.

**For the operator**, swain captures intent, structures it into reviewable artifacts, surfaces what needs a decision, and preserves the *why* behind choices — decision history that can't be derived from the codebase alone.

**For the agent**, swain provides alignment — acceptance criteria, scope boundaries, constraints, and dependency graphs — then verifies outcomes against those criteria. How the agent works internally is irrelevant; any agent that reads markdown can participate.

Two questions drive the entire system:

1. **"What needs a decision?"** — the operator's question.
2. **"What's ready for implementation?"** — the agent's question.

## Problem Statement

AI coding agents are fast but stateless. Without a structured system of record, decisions pile up, agents implement against stale intent, and the reasoning behind past choices is lost. The gap isn't code quality — it's the coordination layer between human decisions and agent execution.

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
