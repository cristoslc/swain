---
title: "Diagnostic Recovery Interaction Flow"
artifact: DESIGN-011
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

# Diagnostic Recovery Interaction Flow

## Design Intent

*   **Context**: We deleted `systematic-debugging` from external skills. All automated repair now uses a global rule in `AGENTS.md`.
*   **Goals**: Fix the user experience of agents randomly guessing solutions. Make sure an agent explicitly tells the user its hypothesis when an error occurs.
*   **Constraints**: Keep the debugging loop isolated. Read the full error before rewriting a file.
*   **Non-goals**: We are not building visual stack traces. 

## Interaction Surface

This covers how the agent converses globally when a script crashes.

### Debugging Loop Pattern

**Happy Path (Agent correctly isolates cause):**
1. Agent runs an integration test. Output drops a "Syntax error" dump.
2. Agent reads `AGENTS.md` debug rules.
3. Agent replies to user: "The test failed deeply inside the auth helper. I hypothesis a missing parent brace. Let me isolate it."
4. Agent opens a target file to verify its hypothesis.
5. Agent patches the single file rather than a total rewrite.
6. Agent runs isolated unit test. It passes.
7. Agent replies to user: "Syntax error fixed. Resuming larger test."

**Sad Path (Agent guesses wrongly):**
1. Agent encounters an error. It attempts three fixes without printing logic.
2. The user sees a blocked state.
3. The user prompts the agent to halt and define a clear hypothesis before editing further.
