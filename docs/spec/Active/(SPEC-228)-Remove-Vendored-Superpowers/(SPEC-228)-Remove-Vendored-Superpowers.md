---
title: "Remove Vendored Superpowers Chaining"
artifact: SPEC-228
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

# Remove Vendored Superpowers Chaining

## Problem / Opportunity

Currently, `swain-*` programs check for `superpowers` files before they start acting. These files include `brainstorming.md`, `writing-plans.md`, and `test-driven-development.md`. We want to build these habits natively. So we must drop the file checks and remote chains to keep things clean.

## Proposed Solution

- Search for and delete `superpowers` text chains inside the `.agents/skills/` paths.
- Keep only the core scripts that start with `swain-`.
- Remove lines that say `brainstorming → swain-design` or `writing-plans → swain-do` inside `.claude/skills/swain-design/SKILL.md` and related guides.

## Acceptance Criteria

1. No `swain-*` skill checks if `.agents/skills/superpowers` is present.
2. The core rules operate on their own without calling external files.
3. The modifications to `swain` skills must undergo an audit by the `writing-skills` skill (or equivalent skill-creator), including at least one round of optimization and behavioral testing.

## Technical Details

- Use standard multiedit tools to scrub script references from `swain-design` and `swain-do`.
- Fully delete the vendored skill copies inside `.agents/skills` and `.claude/skills` that do not start with `swain-`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
| Active | 2026-04-02 | TBD | Approved and transitioned |
