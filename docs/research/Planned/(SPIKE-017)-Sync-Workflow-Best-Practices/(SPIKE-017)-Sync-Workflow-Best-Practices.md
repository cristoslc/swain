---
title: "Sync Workflow Best Practices"
artifact: SPIKE-017
status: Planned
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
question: "Beyond fetch-first and security scanning, what workflow habits should swain-sync enforce or encourage for clean, safe git collaboration?"
gate: Pre-EPIC-012-specs
risks-addressed:
  - Missing workflow habits that other tools enforce by default
  - Over-engineering the sync workflow with rarely useful checks
linked-artifacts:
  - EPIC-012
evidence-pool: ""
---

# Sync Workflow Best Practices

## Question

Beyond fetch-first and security scanning, what workflow habits should swain-sync enforce or encourage for clean, safe git collaboration?

## Go / No-Go Criteria

- **GO:** At least 2 additional habits identified that meaningfully reduce foot-gun risk in solo or small-team workflows
- **NO-GO:** All additional habits add friction without measurable safety improvement — keep swain-sync focused on fetch-first + security scanning

## Pivot Recommendation

If no additional habits are worth enforcing, keep swain-sync lean and document the "nice-to-have" practices in a runbook instead of baking them into the tool.

## Areas to investigate

- Stash/pop dirty working tree handling
- Rebase vs merge strategy configuration
- Branch protection awareness (don't push to protected branches)
- Commit message linting / conventional commits enforcement
- Pre-push hook verification
- Conflict resolution strategies
- Large file detection (prevent accidental binary commits)
- Sign-off / GPG signing enforcement

## Findings

(Populated during Active phase)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | 34f2d62 | Initial creation |
