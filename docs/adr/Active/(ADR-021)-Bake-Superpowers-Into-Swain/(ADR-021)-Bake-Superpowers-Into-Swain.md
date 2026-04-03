---
title: "Bake Superpowers Practices into Core Swain without Vendored Chaining"
artifact: ADR-021
track: standing
status: Active
author: Assistant
created: 2026-04-01
last-updated: 2026-04-01
linked-artifacts:
  - EPIC-053
  - DESIGN-008
depends-on-artifacts: []
evidence-pool: ""
---

# Bake Superpowers Practices into Core Swain without Vendored Chaining

## Context

Swain uses "superpowers" skills today. These include planning, testing, and brainstorming skills. We currently copy these external scripts into our project workspace. This causes copyright risks. It also makes updates hard. But the practices inside them are standard. Socratic planning, checking paths, and debugging are normal tasks. We can bake these standard practices directly into Swain's core skills. We do not need the external files.

## Decision

We will delete all checks for external scripts. We will remove external hooks from `swain` skills. We will add the core methods directly to our tools:
1. **Socratic Discovery**: We will require `swain-design` to explore options before it drafts new documents.
2. **Implementation Planning**: We will require `swain-do` to make strict task lists before it codes.
3. **Verification Gates**: We will make sure `swain-do` runs tests. It must show passing output before a task is done.
4. **Global Debugging Loop**: We will add a strict test loop rule inside `AGENTS.md`.

## Alternatives Considered

1. **Rewrite Superpowers**: We could rewrite the external skills from scratch. We rejected this because it keeps the complex chaining design. We want a simpler setup.
2. **Seek IP Waivers**: We could ask authors for permission. We rejected this because it holds back Swain as a free tool.

## Consequences

- **Positive**: Swain becomes self-contained. It needs no extra downloads.
- **Positive**: Agents work faster without passing tasks between skills.
- **Negative**: We must update our own core loops if best practices change.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-01 | TBD | Initial creation |
| Active | 2026-04-02 | TBD | Approved and transitioned |
