---
title: "Doctor Trunk/Release Migration Detection"
artifact: SPEC-137
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
---

# Doctor Trunk/Release Migration Detection

## Goal

Add preflight and doctor detection for repos that haven't adopted the trunk+release branch model (ADR-013). Advisory only — does not block other checks.

## Deliverables

### Preflight (swain-preflight.sh)
- Check `scripts/swain-trunk.sh` exists and is executable
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
