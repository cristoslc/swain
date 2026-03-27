---
title: "Design Intent Template Section"
artifact: SPEC-095
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: ""
parent-epic: EPIC-035
parent-initiative: ""
linked-artifacts:
  - SPEC-097
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Design Intent Template Section

## Problem Statement

DESIGN artifacts have no mechanism to preserve the original design vision. As mutable sections (flows, states, screens) evolve, the reasoning behind the original design is lost. There's no stable criteria set against which to evaluate whether implementation changes constitute drift or intentional evolution.

## External Behavior

Add a `## Design Intent` section to the DESIGN template, immediately after the title and before Interaction Surface:

```markdown
## Design Intent

**Context:** [One sentence anchoring the design to its user-facing purpose]

### Goals
- [What experience we're trying to create]

### Constraints
- [Machine-checkable or reviewable boundaries]

### Non-goals
- [What we explicitly decided NOT to do]
```

**Write-once convention:** Design Intent is established when the DESIGN is created or transitions to Active. It is not updated when the mutable sections evolve. If the intent itself fundamentally changes, the DESIGN should be Superseded and a new one created.

Write-once is enforced by agent convention, not tooling. The structured format makes unintentional edits obvious in code review.

## Acceptance Criteria

- **Given** the DESIGN template, **When** updated, **Then** it includes a Design Intent section with Context, Goals, Constraints, and Non-goals subsections
- **Given** the DESIGN definition, **When** updated, **Then** it documents the write-once convention and the Supersede-on-intent-change rule
- **Given** an existing active DESIGN artifact, **When** a SPEC transitions to Implementation and links to that DESIGN, **Then** the agent surfaces the Design Intent (Goals, Constraints, Non-goals) for alignment awareness
- **Given** the swain-design skill, **When** creating a new DESIGN, **Then** it prompts for Design Intent content during creation

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Update `references/design-template.md.template` — add Design Intent section
- Update `references/design-definition.md` — document write-once convention
- Update swain-design SKILL.md workflow — prompt for intent during DESIGN creation
- No tooling enforcement of write-once — agent convention only

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Created from EPIC-035 decomposition |
