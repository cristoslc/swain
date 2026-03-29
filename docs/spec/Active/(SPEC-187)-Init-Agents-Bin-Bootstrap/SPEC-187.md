---
title: "Init .agents/bin/ Bootstrap"
artifact: SPEC-187
track: implementation
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
parent-epic: EPIC-047
priority-weight: medium
depends-on-artifacts:
  - SPEC-186
linked-artifacts:
  - ADR-019
---

# Init .agents/bin/ Bootstrap

## Goal

swain-init creates `.agents/bin/` and populates it with symlinks during project onboarding. This ensures new projects have working agent-facing script resolution from the first session.

## Behavior

During swain-init's onboarding flow (after skill installation, before first session):

1. Create `.agents/bin/` if it doesn't exist
2. Scan `skills/*/scripts/` for agent-facing scripts (same discovery logic as SPEC-186)
3. Create relative symlinks for each discovered script
4. Add `.agents/bin/` to `.gitignore` if not already present (consumer projects should not track these symlinks — they're regenerated from the skill tree)

### Idempotency

If `.agents/bin/` already exists (e.g., from a previous init or doctor repair), skip existing valid symlinks and only create missing ones. Never fail on an already-populated directory.

## Deliverables

- Updated `swain-init/SKILL.md` — new step in onboarding flow for `.agents/bin/` setup
- `.gitignore` entry for `.agents/bin/` in consumer projects

## Test Plan

- T1: Fresh init on a project with no `.agents/bin/` — directory created, symlinks populated
- T2: Re-init on a project with existing `.agents/bin/` — no errors, missing symlinks added
- T3: `.gitignore` includes `.agents/bin/` after init

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Created as EPIC-047 child |
