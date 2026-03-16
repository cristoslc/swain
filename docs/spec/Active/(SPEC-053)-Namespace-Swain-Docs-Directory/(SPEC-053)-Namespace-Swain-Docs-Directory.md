---
title: "Namespace Swain Docs Directory"
artifact: SPEC-053
track: implementable
status: Active
author: cristos
created: 2026-03-15
last-updated: 2026-03-15
type: task
parent-epic: ""
parent-initiative: INITIATIVE-001
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Namespace Swain Docs Directory

## Problem Statement

Swain's artifact directories (`docs/spec/`, `docs/epic/`, `docs/adr/`, etc.) sit at the top level of `docs/`, which collides with host repo documentation when swain is installed in a project that already has its own `docs/` structure. A host repo with `docs/adr/` for its own ADRs would conflict with swain's `docs/adr/`. This makes swain a bad tenant.

## External Behavior

Move all swain-managed artifact directories under a namespace to prevent collisions. Two options to decide between:

**Option A: Subfolder** — `docs/swain/spec/`, `docs/swain/epic/`, `docs/swain/adr/`, etc.

**Option B: Prefix** — `docs/swain-spec/`, `docs/swain-epic/`, `docs/swain-adr/`, etc.

Either approach ensures swain's artifacts don't collide with the host repo's documentation. The chosen approach must be applied consistently across:
- All artifact type directories (spec, epic, adr, vision, initiative, journey, persona, research, design, runbook)
- All skill scripts that reference `docs/` paths (specgraph, specwatch, adr-check, etc.)
- All artifact definitions and templates that document folder structure
- AGENTS.md and any path references in skill SKILL.md files
- Index files (`list-*.md`)

## Acceptance Criteria

1. Given swain is installed in a repo with its own `docs/` directory, when swain creates artifacts, then no path collision occurs with the host repo's documentation.

2. Given the namespace migration is applied, when all existing specgraph/specwatch/adr-check scripts run, then they find artifacts at the new paths without error.

3. Given existing artifacts exist at old paths, when the migration runs, then artifacts are moved to new paths with git history preserved (via `git mv`).

4. Given swain-doctor runs after migration, when old-path artifacts exist, then it detects them and offers remediation guidance.

## Scope & Constraints

**In scope:**
- Choose namespace approach (subfolder vs prefix)
- Migration script to move existing artifacts
- Update all path references in scripts, definitions, templates, and skill files
- swain-doctor detection of old-path artifacts

**Out of scope:**
- Changing the artifact type names or folder structures within each type directory

**Constraints:**
- Must preserve git history via `git mv`
- Must include a migration path (per AGENTS.md migration policy)

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-15 | — | Initial creation |
