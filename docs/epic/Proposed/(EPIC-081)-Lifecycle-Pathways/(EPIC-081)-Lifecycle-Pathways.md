---
title: "Lifecycle Pathways"
artifact: EPIC-081
track: container
status: Proposed
author: cristos
created: 2026-04-18
last-updated: 2026-04-18
parent-vision: 004
parent-initiative: INITIATIVE-002
priority-weight: high
success-criteria:
  - Shippers have legitimate fast paths that work with the system rather than against it
  - Artifacts stuck in non-terminal phases beyond a configurable threshold are surfaced for triage
  - Low-complexity work can reach Complete without disproportionate ceremony
  - Previously validated patterns can be reused without full ceremony on each repetition
depends-on-artifacts:
  - PERSONA-003
  - PERSONA-004
addresses: []
evidence-pool: ""
---

# Lifecycle Pathways

## Goal / Objective

Create legitimate velocity pathways within the artifact lifecycle so that Shippers can move fast without fighting the system, while Builders retain the verification gates they need for quality. Currently, the only fast path skips specwatch scanning — there's no structural accommodation for hotfixes, retroactive documentation, or previously validated patterns. This epic merges concerns about velocity accommodation (from the Shipper evaluation) and organizational debt prevention (from both evaluations).

## Desired Outcomes

- **Shippers** can ship production bugs through a hotfix lane without 10 ceremony steps.
- **Shippers** can create retroactive specs for work they already built, capturing decisions after the fact.
- **Builders** benefit from artifacts being triaged regularly, preventing accumulation of stale Active items.
- **Both personas** benefit from ceremony that scales with risk, not ceremony that applies uniformly regardless of complexity.

## Progress

<!-- Auto-populated from session digests. -->

## Scope Boundaries

**In scope:**
- Hotfix lane (`--hotfix` or `--fire` flag) for SPECs with `type: bug` or `type: fix` and no parent epic
- Retroactive SPEC creation (`--retroactive` flag) that scans recent git commits and backfills
- `swain-do: required | optional | skip` field on SPECs (default stays `required`)
- Fast-path verification: low-complexity SPECs can skip Needs Manual Test
- Artifact staleness detection in specwatch (`STALE_PHASE` finding type)
- Collapsed hash stamping for fast-path-eligible artifacts

**Out of scope:**
- New artifact types (CHORE already handles lightweight non-feature work)
- EXPERIMENT artifact type (tracked in EPIC-079)
- CI/deployment hooks (tracked in EPIC-079)
- Verification gate changes (tracked in EPIC-078)
- Renaming SPEC types or CHORE

## Child Specs

_To be decomposed when the epic transitions to Active._

## Key Dependencies

- Fast-path tier detection (SPEC-045) already exists and should be extended
- The `swain-do` frontmatter field on SPECs must be extended
- `specwatch.sh` must be extended with staleness detection
- PERSONA-003 and PERSONA-004 evaluations inform the design

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-04-18 | — | Created from Builder/Shipper persona evaluation |