---
title: "Structural Cross-Skill Invariant Tests"
artifact: SPEC-265
track: implementation
status: Proposed
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
linked-artifacts:
  - ADR-030
depends-on-artifacts: []
evidence-pool: ""
---

# Structural Cross-Skill Invariant Tests

## Context

During the ADR-030 migration (deprecating swain-session), we discovered that 30+ cross-skill references needed updating. The BDD test suite written for ADR-030 (66 assertions) caught these effectively using grep-based structural checks. This pattern should be generalized into a standing test suite that runs on every commit touching skill files.

## Goal

Create a test suite that validates structural invariants across all swain skills. These are properties that should always hold, not specific to any one migration.

## Acceptance Criteria

- [ ] AC1: A test file `tests/test_skill_invariants.sh` exists and is executable
- [ ] AC2: Tests validate that every skill SKILL.md has valid YAML frontmatter (name, description, allowed-tools)
- [ ] AC3: Tests validate that the meta-router (`skills/swain/SKILL.md`) has a row for every installed skill directory
- [ ] AC4: Tests validate that session-check preambles across all skills reference the same startup command (currently `/swain-init`)
- [ ] AC5: Tests validate that `AGENTS.md`, `AGENTS.content.md`, and the meta-router routing tables are consistent with each other
- [ ] AC6: Tests validate that `tool-availability.md` references only skills that exist
- [ ] AC7: Tests pass on the current codebase
- [ ] AC8: Tests run in under 5 seconds (grep-based, no network, no git operations)

## Out of Scope

- Runtime behavior testing (that belongs in per-skill test suites)
- CI integration (can be added later)
- Automated fix suggestions (report-only)

## Lifecycle

| Hash | Transition | Date |
|------|-----------|------|
