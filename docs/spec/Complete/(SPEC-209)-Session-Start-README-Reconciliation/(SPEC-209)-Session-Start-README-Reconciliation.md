---
title: "Session-Start README Reconciliation"
artifact: SPEC-209
track: implementable
status: Complete
author: operator
created: 2026-03-31
last-updated: 2026-03-31
priority-weight: ""
type: feature
parent-epic: EPIC-050
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-207
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Session-Start README Reconciliation

## Problem Statement

README drift accumulates silently. The README promises features that were dropped, describes behavior that changed, or omits capabilities that were added. No session-start checkpoint catches this.

## Desired Outcomes

At the start of each session, when swain-session picks a focus lane, the operator sees specific mismatches between README claims and artifact state.

## External Behavior

At focus lane selection, read README.md and extract claims. Compare against Active artifacts. Surface mismatches as specific questions. Reconciliation is bidirectional. Deferrals are tracked and raised next session.

## Acceptance Criteria

- Given a README that claims a dropped feature, when swain-session runs, then the mismatch is surfaced.
- Given a deferred mismatch, then it is raised again next session.
- Given a resolved mismatch, then it is not raised again.
- Given no drift, then the check passes silently.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Reconciliation section in SKILL.md | Haiku agent verified section with trigger, process, deferral tracking | PASS |
| Deferral schema in session.json | Haiku agent confirmed readme_deferrals key spec | PASS |
| Correct placement in skill | Between Session.json schema and Session Lifecycle | PASS |

## Scope & Constraints

- Depends on semantic extraction from SPEC-207.
- Deferral state persists in session.json.
- Runs only at focus lane selection, not continuously.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | 61379ba | Reconciliation checkpoint in swain-session SKILL.md |
