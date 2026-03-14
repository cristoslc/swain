---
title: "Rename swain-design to swain-commission"
artifact: EPIC-019
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
parent-vision: VISION-001
success-criteria:
  - Skill directory renamed from skills/swain-design/ to skills/swain-commission/
  - All internal references updated (AGENTS.md, swain meta-router, swain-search, swain-do, swain-help, swain-doctor, swain-init)
  - SKILL.md name, description, and trigger patterns reflect the new name
  - swain-doctor detects stale swain-design references in adopter projects and offers migration guidance
  - swain-update handles the rename cleanly when pulling new versions (old skill directory removed, new one installed)
  - skills-lock.json updated with new skill name
  - Existing docs/artifacts that reference swain-design by name are updated
  - Migration path documented in release notes per project policy (ADR-002 precedent)
  - swain-design name is freed for future use as a frontend orchestrator skill
depends-on-artifacts: []
addresses: []
evidence-pool: ""
---

# Rename swain-design to swain-commission

## Goal / Objective

Rename the artifact lifecycle skill from `swain-design` to `swain-commission`. The current name no longer describes the skill's scope (it manages the full artifact lifecycle, not just "design"), and the `swain-design` name is needed for a planned frontend orchestrator skill.

"Commission" comes from nautical terminology — formally authoring a vessel's purpose and putting it into service — which fits swain's boatswain etymology. The skill's primary identity is **authoring** artifacts that capture operator intent (visions, epics, specs, spikes, ADRs, personas, runbooks, journeys).

## Scope Boundaries

**In scope:**
- Rename skill directory and all internal metadata
- Update all cross-references in other swain skills
- Update AGENTS.md governance rules and skill routing table
- Update swain meta-router to route `swain-commission` instead of `swain-design`
- swain-doctor detection: warn when stale `swain-design` references exist in adopter projects
- swain-update migration: clean removal of old skill directory, install of new one
- Release notes with migration path documentation
- Update skills-lock.json

**Implementation note:** This rename should be implemented in a git worktree to isolate the breaking change from main until ready.

**Out of scope:**
- Building the new swain-design frontend orchestrator (separate epic)
- Renaming artifact types or changing artifact lifecycle phases
- Changing the skill's functional behavior (this is a rename, not a rewrite)

## Child Specs

_To be created during implementation planning._

Anticipated specs:
1. Core rename — directory, SKILL.md, meta-router, AGENTS.md
2. Cross-reference updates — all skills that reference swain-design
3. swain-doctor stale reference detection
4. swain-update migration path (old → new skill directory)
5. Release notes and changelog

## Key Dependencies

- This is a breaking change — requires a major version bump per project migration policy
- ADR-002 precedent: the bd → tk rename established the migration pattern (doctor detection + update cleanup)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Decision from naming brainstorm session |
