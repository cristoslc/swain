---
title: "Remove swain-session Skill Directory"
artifact: SPEC-264
track: implementation
status: Proposed
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
linked-artifacts:
  - ADR-023
depends-on-artifacts:
  - ADR-023
evidence-pool: ""
---

# Remove swain-session Skill Directory

## Context

ADR-023 deprecated swain-session by distributing its responsibilities to swain-init, swain-teardown, swain-roadmap, swain-do, swain-retro, swain-sync, and swain-release. The skill directory (`skills/swain-session/`) still exists on disk. It contains the deprecated SKILL.md and a `scripts/` directory with utility scripts that other skills depend on via `.agents/bin/` symlinks.

## Goal

Delete `skills/swain-session/` without breaking the utility scripts that live there. Most scripts are already symlinked from `.agents/bin/`. Any that are not must be relocated before deletion.

## Acceptance Criteria

- [ ] AC1: `skills/swain-session/SKILL.md` is deleted
- [ ] AC2: `skills/swain-session/tests/` is deleted or relocated to `tests/`
- [ ] AC3: Every script in `skills/swain-session/scripts/` that has a symlink in `.agents/bin/` is relocated to a surviving skill's `scripts/` directory, and the symlink is updated
- [ ] AC4: Scripts without symlinks are either relocated or confirmed unused and deleted
- [ ] AC5: `swain-session` is removed from `skills/swain-doctor/references/legacy-skills.json` or added as a legacy entry
- [ ] AC6: No remaining skill files import, source, or reference `skills/swain-session/` as a path (historical docs excluded)
- [ ] AC7: Existing tests pass after deletion

## Out of Scope

- Renaming the utility scripts themselves (e.g., `swain-session-check.sh` keeps its name)
- Changing the session-state JSON schema
- Modifying any behavior — this is a file relocation, not a rewrite

## Lifecycle

| Hash | Transition | Date |
|------|-----------|------|
