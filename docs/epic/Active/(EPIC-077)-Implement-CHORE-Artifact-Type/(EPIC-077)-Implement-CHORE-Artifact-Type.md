---
title: "Implement CHORE Artifact Type"
artifact: EPIC-077
track: container
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
linked-artifacts:
  - [ADR-045](../../adr/Active/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type/(ADR-045)-Chores-As-A-Lightweight-Artifact-Type.md)
  - [ADR-027](../../adr/Active/(ADR-027)-All-Artifacts-Must-Be-Foldered/(ADR-027)-All-Artifacts-Must-Be-Foldered.md)
  - [ADR-003](../../adr/Active/(ADR-003)-Normalize-Artifact-Lifecycle-to-Three-Tracks/(ADR-003)-Normalize-Artifact-Lifecycle-to-Three-Tracks.md)
depends-on-artifacts: []
priority-weight: medium
success-criteria:
  - "CHORE prefix recognized by all artifact scripts (next-id, detect-duplicates, resolve-link, relink)"
  - "specgraph builds, queries, and renders CHORE artifacts correctly"
  - "specwatch detects and validates CHORE artifacts"
  - "rebuild-index generates list-chores.md"
  - "swain-design SKILL.md documents CHORE as a first-class type"
  - "CHORE-001 processes correctly through chart, specwatch, and relink"
---

# Implement CHORE Artifact Type

## Problem Statement

ADR-045 established CHORE-NNN as a new artifact type for lightweight cleanup work. The type is defined and CHORE-001 exists, but the tooling doesn't know about it yet. Scripts, Python modules, and skill docs enumerate known types and would skip CHORE artifacts silently.

## Scope

This EPIC covers the infrastructure to make CHOREs a first-class artifact type in the swain tooling chain. It does not cover executing CHORE-001 (the actual file moves and cleanup).

### In scope

- Bash scripts: prefix case mappings, regex patterns, validation lists
- Python modules: specgraph type inference, xref scanning, materialization
- specwatch: type directory enumeration
- rebuild-index: chores type support and list-chores.md generation
- Skill documentation: swain-design SKILL.md, lifecycle tracks reference

### Out of scope

- Executing CHORE-001 (folder cleanup, relinking, `.tickets/` migration)

## Child Specs

| Spec | Title | Dependency |
|------|-------|------------|
| SPEC-311 | Bash Script Support for CHORE Prefix | None |
| SPEC-312 | Python Tooling Support for CHORE Type | SPEC-311 |
| SPEC-313 | Skill Docs and Index for CHORE Type | SPEC-312 |

## Risk Assessment

Low risk. All changes are additive — adding `CHORE` to lists and regex patterns. No existing behavior breaks. The `materialize.py` path mapping is the one real fix.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
4ce9b173 Initial creation |