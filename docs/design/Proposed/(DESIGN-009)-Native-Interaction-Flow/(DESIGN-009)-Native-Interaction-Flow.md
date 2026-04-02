---
title: "Native Interaction Flow for Agent Planning and Discovery"
artifact: DESIGN-009
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
evidence-pool: ""
sourcecode-refs: []
---

# Native Interaction Flow for Agent Planning and Discovery

## Design Intent

*   **Context**: Swain is dropping external skills for its own planning and discovery. The interaction with the user changes. We need a clear flow for asking questions before making files.
*   **Goals**: Force the agent to clear up missing details before writing code or large documents. Make sure the user always sees the plan via standard UI tasks.
*   **Constraints**: The agent must not guess major limits. The agent must show two or more clear options when it asks questions. Keep chat loops short.
*   **Non-goals**: We are not building a custom GUI. We are relying on standard chat and standard task lists.

## Interaction Surface

This section covers the exact flows a user will see during `swain-design` and `swain-do`.

### 1. Socratic Discovery Flow (`swain-design`)

**Happy Path (User gives intent):**
1. User says: "Create a new Epic for user login."
2. Agent reads `swain-design` rules.
3. Agent replies: "To build the user login Epic, I need to know the limits. Option A: Full OAuth with Google/GitHub. Option B: Simple email and password. Which path do you want? And are there any tight deadlines?"
4. User says: "Option B. No deadlines."
5. Agent writes the Epic file to disk.

**Sad Path (User ignores questions):**
1. User replies: "Just build it."
2. Agent replies: "I must define limits first to avoid bad code. I will assume Option B (email only). Do you agree?"
3. Agent waits for a firm "yes" before writing the file.

### 2. Implementation Checklist Flow (`swain-do`)

**Happy Path:**
1. User says: "Start work on SPEC-228."
2. Agent reads the target SPEC.
3. Agent uses the `todos` tool to post a visible checklist to the user UI.
   - Task 1: "Write a test."
   - Task 2: "Apply fix."
   - Task 3: "Verify tests pass."
4. User sees the list. Agent begins work on Task 1.

### 3. Verification Hand-off 

**Happy Path:**
1. Agent completes the code.
2. Agent runs the test suite. 
3. Terminal shows a green passing state.
4. Agent marks the final task complete.
5. Agent says to the user: "Code is done and verified."
