---
title: "Native Socratic Discovery in swain-design"
artifact: SPEC-230
track: implementable
status: Active
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

The old method chained `brainstorming` before making plans. We need to add this rule straight to `swain-design`. By doing so, we ensure generated goals are sound and explored well.

## Proposed Solution

- Build a hard Socratic Discovery rule into `swain-design`.
- At the exact moment a worker asks for a new Epic, the agent MUST detail at least two other paths before writing. It must secure limits directly with the user.
- Mix probing questions ("Why?" "What stops this?") into the core `swain-design` creation guide.

## Acceptance Criteria

1. `swain-design` requires a pause to discover lines before writing high-level artifacts.
2. The agent outputs exact limits or issues to the human if they remain untold.
3. Remove the explicit test for `.claude/skills/brainstorming/SKILL.md`.
4. The modified `swain-design` skill must undergo an audit by the `writing-skills` skill. This includes one round of tuning and testing.

## Technical Details

- Append Socratic Sourcing facts to `swain-design/SKILL.md` under "Creating artifacts" as Step 0.
- Shape the output rule so the agent escapes chat loops quickly after the user confirms.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
| Active | 2026-04-02 | TBD | Approved and transitioned |
