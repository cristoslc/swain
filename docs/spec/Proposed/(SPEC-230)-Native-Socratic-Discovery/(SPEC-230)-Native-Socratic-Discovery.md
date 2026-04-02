---
title: "Native Socratic Discovery in swain-design"
artifact: SPEC-230
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

# Native Socratic Discovery in swain-design

## Problem / Opportunity

The old method chained `brainstorming` before making plans to make sure it tested options. We need to add this directly to `swain-design`. In doing so, we ensure generated goals are sound and fully explored.

## Proposed Solution

- Build a mandatory Socratic Discovery rule into `swain-design`.
- At the moment an operator asks for a new Epic, the agent MUST detail at least two other paths before writing. It must secure limits directly with the user.
- Mix probing questions ("Why?" "What restricts this?") into the core `swain-design` creation guide.

## Acceptance Criteria

1. `swain-design` requires a pause for discovery before writing top-level artifacts.
2. The agent outputs exact limits or issues to the human if they remain untold.
3. Remove the explicit test for `.claude/skills/brainstorming/SKILL.md`.
4. The modified `swain-design` skill must undergo an audit by the `writing-skills` skill (or equivalent skill-creator), including at least one round of optimization and behavioral testing.

## Technical Details

- Append Socratic Sourcing facts to `swain-design/SKILL.md` under "Creating artifacts" as Step 0.
- Shape the output rule so the agent escapes chat loops quickly after the user confirms.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
