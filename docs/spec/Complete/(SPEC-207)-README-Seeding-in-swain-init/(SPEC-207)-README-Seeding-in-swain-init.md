---
title: "README Seeding in swain-init"
artifact: SPEC-207
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
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# README Seeding in swain-init

## Problem Statement

A new project has code but no README. Or it has a README but no artifacts. Swain-init currently ignores the README — it doesn't seed one if missing, and it doesn't extract intent from an existing one. This leaves early-phase projects with no alignment anchor.

## Desired Outcomes

After swain-init runs, the project always has a README. When the artifact tree is empty or thin, the operator gets proposed seed artifacts extracted from README content — Visions, Personas, Journeys, and Designs. The operator reviews and approves each proposal.

## External Behavior

**README creation (when missing):** swain-init checks for README.md at the repo root. If absent, it seeds one based on context — interview the operator, infer from code, or compile from artifacts.

**Artifact seeding (when README exists but tree is empty/thin):** Read the README as prose, extract claims, and propose seed artifacts (Vision, Personas, Journeys, Designs). The operator approves, edits, or rejects each.

**Semantic extraction:** Read the entire README as prose. No convention-based sections or markers. Any claim is a potential intent source.

## Acceptance Criteria

- Given a repo with no README.md, when swain-init runs, then it prompts the operator and seeds a README based on available context.
- Given a repo with a README but no artifacts, when swain-init runs, then it proposes at least one seed artifact.
- Given a repo with both README and artifacts, when swain-init runs, then it skips seeding and proposals.
- Given proposed seed artifacts, when the operator rejects one, then it is not created.
- Given proposed seed artifacts, when the operator edits one before approving, then the edited version is created.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Phase 5.5 exists in SKILL.md | Haiku agent verified section with Steps 5.5.1-5.5.3 | PASS |
| Context detection scripts run | Scripts execute without error in test | PASS |
| Summary includes README lines | Haiku agent confirmed summary entries | PASS |

## Scope & Constraints

- The semantic extraction logic is shared with SPEC-209, SPEC-210, and SPEC-211.
- Swain never silently rewrites the README.
- No README structure or template is imposed.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-31 | — | Initial creation |
| Complete | 2026-03-31 | 61379ba | Implemented in swain-init SKILL.md Phase 5.5 |
