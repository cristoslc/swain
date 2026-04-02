---
title: "Global Debugging Loop in AGENTS.md"
artifact: SPEC-231
track: implementable
status: Proposed
author: Assistant
created: 2026-04-01
last-updated: 2026-04-01
priority-weight: "high"
type: "enhancement"
parent-epic: EPIC-053
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - ADR-021
addresses: []
---

# Global Debugging Loop in AGENTS.md

## Problem / Opportunity

To stop using `systematic-debugging`, we need a strong fixing rule across all Swain skills. When scripts die or bash throws code 1, the agent needs a known repair path. Random code guessing breaks trust. 

## Proposed Solution

- Overhaul `AGENTS.md` (the core rulebook) with a new group: "Global Debugging Methodology".
- State the Isolate -> Hypothesize -> Test rule for all tools inside Swain.
- Command the agent to read all failing text and form test edges before rewriting large code files.

## Acceptance Criteria

1. `AGENTS.md` exhibits a rigid fixing path.
2. The manual expressly bans changing unrelated bugs or adding random fix lines without testing ideas.
3. This fills the role of the deleted `systematic-debugging` feature entirely.

## Technical Details

- Inject the fix pattern near the bottom of `AGENTS.md` in the root checkout.
- Format the instruction with bold modal words ("MUST", "NEVER") consistent with older rules.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
