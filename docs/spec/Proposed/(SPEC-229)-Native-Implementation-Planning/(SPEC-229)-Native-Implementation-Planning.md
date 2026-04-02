---
title: "Native Implementation Planning in swain-do"
artifact: SPEC-229
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

# Native Implementation Planning in swain-do

## Problem / Opportunity

By dropping the `writing-plans` skill, `swain-do` needs its own check loop. It must build a rigid checklist before it alters a project.

## Proposed Solution

- Update `swain-do` to order a checklist. It must complete the list before writing changes.
- The standard agent `todos` tool can list these tasks natively.
- Enforce the `test-driven-development` rule inside `swain-do`: the first stage of an implementation must write a failing loop test.

## Acceptance Criteria

1. `swain-do/SKILL.md` requires forming a task outline before accessing root files.
2. Code may not change until a check command, such as testing or linting, sits on the list.
3. Check results must appear and show a real success signal before marking the task finished.

## Technical Details

- Add a strict planning section into `swain-do/SKILL.md`. Overwrite the previous `writing-plans` transition section.
- Put failure rules directly in text: "If execution halts, jump into the Global Debugging Loop inside AGENTS.md rather than giving up."

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
