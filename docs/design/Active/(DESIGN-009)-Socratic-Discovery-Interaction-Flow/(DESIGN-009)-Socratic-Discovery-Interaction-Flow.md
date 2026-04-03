---
title: "Socratic Discovery Interaction Flow"
artifact: DESIGN-009
domain: interaction
track: standing
status: Active
author: Assistant
created: 2026-04-01
last-updated: 2026-04-01
linked-artifacts:
  - EPIC-053
  - ADR-021
depends-on-artifacts: []
sourcecode-refs: []
---

# Socratic Discovery Interaction Flow

## Design Intent

*   **Context**: We dropped the external `brainstorming` skill. Now `swain-design` handles its own discovery process.
*   **Goals**: Force the agent to ask the user clarifying questions before writing an Epic or Vision.
*   **Constraints**: Keep chat loops brief. Only ask bounds and limits. Present two distinct options to the user.
*   **Non-goals**: We are not designing graphical screens. This is a text flow.

## Interaction Surface

This section covers the exact chat flow for artifact creation.

### Socratic Pattern

**Happy Path (User states goals):**
1. User says: "Create a new Epic for user login."
2. Agent reads `swain-design` rules.
3. Agent replies: "To build the user login Epic, I need to know the limits. Option A: Full OAuth with Google/GitHub. Option B: Simple email and password. Which path do you want? Are there tight deadlines?"
4. User says: "Option B. No deadlines."
5. Agent writes the Epic file to disk.

**Sad Path (User skips questions):**
1. User replies: "Just build it."
2. Agent replies: "I must define limits first to avoid bad assumptions. I will assume Option B (email only). Do you agree?"
3. Agent waits for a final "yes" before writing the file.
| Active | 2026-04-02 | TBD | Approved and transitioned |
