---
title: "README Existence Check in swain-doctor"
artifact: SPEC-208
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

# README Existence Check in swain-doctor

## Problem Statement

swain-doctor validates project health on every session but does not check for a README. A missing README means the alignment loop has no public intent anchor, yet nothing flags this.

## Desired Outcomes

The operator learns immediately when a README is missing, as part of the standard doctor health check.

## External Behavior

swain-doctor adds a check: does README.md exist at the repo root? If missing, emit a warning. If present, pass silently. Existence check only — no content analysis.

## Acceptance Criteria

- Given a repo with no README.md, when swain-doctor runs, then it emits a warning.
- Given a repo with a README.md, when swain-doctor runs, then the README check passes silently.
- Given swain-doctor output, when the README warning appears, then it is categorized as a health warning.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| check_readme function in script | Haiku agent verified function exists and runs | PASS |
| Doctor JSON output includes readme check | Live test: status "ok" for swain repo | PASS |
| SKILL.md documents the check | Haiku agent verified section with status values | PASS |

## Scope & Constraints

- Existence check only. Content reconciliation handled by SPEC-209, SPEC-210, SPEC-211.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | 61379ba | check_readme in doctor script + SKILL.md section |
