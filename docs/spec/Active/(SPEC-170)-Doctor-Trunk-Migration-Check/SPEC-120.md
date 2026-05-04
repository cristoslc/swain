---
title: "Doctor Trunk/Release Migration Detection"
artifact: SPEC-170
track: implementation
status: Active
author: cristos
created: 2026-03-21
last-updated: 2026-03-21
parent-epic: EPIC-029
priority-weight: medium
depends-on-artifacts:
  - SPEC-147
linked-artifacts:
  - EPIC-029
  - ADR-013
  - ADR-019
---

# Doctor Trunk/Release Migration Detection

## Goal

Add preflight and doctor detection for repos that haven't adopted the trunk+release branch model (ADR-013). Advisory only — does not block other checks.

## Deliverables

### Preflight (swain-preflight.sh)
- Check `.agents/bin/swain-trunk.sh` exists and is executable (per [ADR-019](../../../adr/Superseded/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md) agent-facing convention)
- Run it and verify the detected trunk branch has a remote
- Check whether a `release` branch exists
- Advisory message pointing to `scripts/migrate-to-trunk-release.sh --dry-run`

### Doctor (SKILL.md)
- New "Trunk/release branch model check" section
- Three detection steps: script exists, remote exists, release branch exists
- Status values: ok / info / warning

## Test Plan

- T1: Preflight on this repo (trunk+release configured) produces no warnings
- T2: Doctor section documented with clear detection/response/status format

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-21 | — | Created as EPIC-029 child |
| Active | 2026-03-28 | — | Updated path to `.agents/bin/` per ADR-019 agent-facing convention |
