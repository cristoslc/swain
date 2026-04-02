---
title: "Task Execution Interaction Flow"
artifact: DESIGN-010
domain: interaction
track: standing
status: Proposed
author: Assistant
created: 2026-04-01
last-updated: 2026-04-01
linked-artifacts:
  - EPIC-053
  - ADR-021
depends-on-artifacts: []
sourcecode-refs: []
---

# Task Execution Interaction Flow

## Design Intent

*   **Context**: We removed external planning skills. Now `swain-do` forces agents to explicitly show task plans via standard checklists.
*   **Goals**: The user must see the steps the agent intends to take before code changes happen. Make sure tests run before closing tasks.
*   **Constraints**: Visual checks rely entirely on the native `todos` UI element. Do not write code before outlining the checklist.
*   **Non-goals**: We are not altering issue tracking states on GitHub or Jira.

## Interaction Surface

This covers how an agent acts inside `swain-do` when implementing a task.

### Checklist Generation

**Happy Path (Agent plans code):**
1. User says: "Start work on SPEC-228."
2. Agent reads the target SPEC.
3. Agent uses the `todos` tool. It generates a visible checklist for the user.
   - Task 1: "Read files."
   - Task 2: "Write tests."
   - Task 3: "Update code."
4. User sees the checklist. Agent starts Task 1.

### Verification Hand-off

**Happy Path (Agent runs tests):**
1. Agent completes the code changes.
2. Agent executes a bash command for tests.
3. Terminal displays green passing results.
4. Agent marks the `todos` tasks as complete.
5. Agent says: "Implementation is complete. Tests pass."
