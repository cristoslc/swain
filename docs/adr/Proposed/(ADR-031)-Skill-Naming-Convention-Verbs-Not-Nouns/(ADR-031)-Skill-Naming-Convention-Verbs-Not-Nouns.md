---
title: "Skill Naming Convention: Verbs Not Nouns"
artifact: ADR-031
track: standing
status: Proposed
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
linked-artifacts:
  - ADR-030
depends-on-artifacts: []
evidence-pool: ""
---

# Skill Naming Convention: Verbs Not Nouns

## Context

swain-session accumulated seven unrelated responsibilities because "session" is a noun that describes a context, not an action. Any feature that needed session context got bolted onto the session skill: startup, shutdown, status dashboard, bookmarks, focus lane, decision recording, progress log, and README reconciliation.

ADR-030 fixed this by splitting session into verb-named skills (init, teardown) and distributing features to purpose-built skills (roadmap, do, retro, sync, release). The pattern is clear: verb-named skills stay focused; noun-named skills accumulate.

## Decision

Name new swain skills by their primary verb, not their domain noun.

**Good:** `swain-init`, `swain-teardown`, `swain-sync`, `swain-search`, `swain-release`
**Avoid:** `swain-session`, `swain-project`, `swain-workspace`, `swain-pipeline`

When a skill's name is a noun (like `swain-roadmap` or `swain-doctor`), it should describe a concrete output or role, not a broad context. "Roadmap" names the artifact it produces. "Doctor" names the role it plays. Neither invites unrelated features the way "session" did.

### Naming test

Before creating a new skill, ask: "Could someone reasonably add an unrelated feature to this skill and justify it by the name?" If yes, the name is too broad. Pick a narrower verb.

## Consequences

- New skills follow verb naming. No new noun-bucket skills.
- Existing skills are not renamed (renaming has high migration cost for low value). The convention applies going forward.
- Code review should flag PRs that add features to a skill outside its verb scope.

## Lifecycle

| Hash | Transition | Date |
|------|-----------|------|
