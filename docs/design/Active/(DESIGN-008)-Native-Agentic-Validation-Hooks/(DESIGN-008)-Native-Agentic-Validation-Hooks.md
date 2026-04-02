---
title: "Native Agentic Validation Hooks"
artifact: DESIGN-008
domain: system
track: standing
status: Active
author: Assistant
created: 2026-04-01
last-updated: 2026-04-01
linked-artifacts:
  - EPIC-053
  - ADR-021
depends-on-artifacts: []
evidence-pool: ""
---

# Native Agentic Validation Hooks

## Design Intent

*   **Context**: Swain relies on external skill scripts like `test-driven-development`. We are bringing these practices into Swain's core rules natively.
*   **Goals**: Bake deep design thinking, code planning, task checking, and strict debugging into `swain-design` and `swain-do`.
*   **Constraints**: Do not violate copyright. Do not copy vendored `superpowers` scripts. Just use normal software engineering methods instead.
*   **Non-goals**: We are not changing the `tk` schema today.

## System Boundaries

This explains how an agent must behave when running Swain skills. These are the rules that define the task interface.

### 1. Mandatory Socratic Discovery (`swain-design`)
Before creating an Epic, Vision, or Initiative, the agent must ask questions.
- **Precondition**: The user wants a new big document.
- **Contract**: The agent must outline two or more paths, state limits, and ask the user to verify. It cannot just write the file without checking first.

### 2. Implementation Planning (`swain-do`)
Before any code changes, `swain-do` needs a strict plan.
- **Precondition**: The user selects a task to build.
- **Contract**: The agent makes a checklist. It must use the `todos` tool. It cannot write code until the checklist exists.

### 3. Native Verification Gates (`swain-do`)
A task needs proof of passing before being closed.
- **Precondition**: The agent ends the task checklist.
- **Contract**: The agent must run tests. The terminal must show a passing state. If it does not, the task stays open.

### 4. Global Debugging Loop (`AGENTS.md`)
A core rule for when scripts fail.
- **Precondition**: A test, tool, or script sends an error.
- **Contract**: The agent must isolate the error. Then it forms an idea of what broke. Then it tests a specific fix. It must not guess blindly.

## API Contracts

There are no web APIs here. The contract lives totally in `SKILL.md` workflow text.

## Error Semantics

- **Failing Verification**: If step 3 fails, the agent must start step 4. The agent cannot close the task.
- **Skipping Discovery**: If step 1 does not happen, the new file is flawed. It must go back to the human for review.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
| Active | 2026-04-02 | TBD | Approved and transitioned |
