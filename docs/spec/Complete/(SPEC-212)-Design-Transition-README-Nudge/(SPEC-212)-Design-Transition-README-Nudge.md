---
title: "Design Transition README Nudge"
artifact: SPEC-212
track: implementable
status: Complete
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: enhancement
parent-epic: EPIC-050
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Design Transition README Nudge

## Problem Statement

When Visions, Designs, Journeys, or Personas transition phases, the README may need updating. No signal fires — the operator must remember to check.

## Desired Outcomes

Artifact transitions that change public-facing claims trigger a soft nudge. Brainstorming uses the README as primary context when no artifacts exist.

## External Behavior

**Nudge:** On Vision, Design, Journey, or Persona phase transitions that change public-facing claims, emit: "README.md may need updating to reflect this change." Informational, not blocking.

**Brainstorming context:** When brainstorming runs for a project with README but fewer than 3 Active artifacts, use README as starting context.

## Acceptance Criteria

- Given a Vision transitioning to Active, then a soft nudge appears.
- Given a Design transitioning to Superseded, then a soft nudge appears.
- Given the nudge appears, when dismissed, then the transition completes.
- Given a project with README but no artifacts, when brainstorming runs, then README is primary context.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Nudge section in SKILL.md | Haiku agent verified trigger conditions for all 4 types | PASS |
| Brainstorming context detection | Script runs: ACTIVE_COUNT=5, HAS_README=yes | PASS |
| Correct placement | After Decision protection hooks, before Trove integration | PASS |

## Scope & Constraints

- Soft signal only — never blocks a transition.
- Brainstorming integration only when superpowers is installed.
- No dependency on semantic extraction — trigger-based, not content-analysis-based.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | 61379ba | README nudge section in swain-design SKILL.md |
