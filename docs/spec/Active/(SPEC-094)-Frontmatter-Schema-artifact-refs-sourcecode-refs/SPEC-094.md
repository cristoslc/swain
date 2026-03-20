---
title: "Frontmatter Schema — artifact-refs, sourcecode-refs, rel types"
artifact: SPEC-094
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-20
type: ""
parent-epic: EPIC-035
parent-initiative: ""
linked-artifacts:
  - SPEC-091
  - SPEC-103
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Frontmatter Schema — artifact-refs, sourcecode-refs, rel types

## Problem Statement

The enriched `linked-artifacts` v2 format (with `rel`, `commit`, `verified` fields) was introduced for TRAIN but is unnamed and conflated with the flat v1 format. DESIGN artifacts need a new `sourcecode-refs` field for tracking implementation files with blob SHA pinning. Both fields need a typed `rel` vocabulary.

## External Behavior

**`artifact-refs`** — replaces enriched `linked-artifacts` v2:

```yaml
artifact-refs:
  - artifact: SPEC-067
    rel: [documents]
    rel-path: ../../spec/Active/(SPEC-067)-Whatever/SPEC-067.md
    commit: abc1234
    verified: 2026-03-19
  - artifact: DESIGN-003
    rel: [aligned]
    rel-path: ../../design/Active/(DESIGN-003)-Whatever/DESIGN-003.md
    commit: def5678
    verified: 2026-03-19
```

**`sourcecode-refs`** — new, DESIGN-only (initially):

```yaml
sourcecode-refs:
  - path: src/components/Button/Button.tsx
    blob: a1b2c3d
    commit: def5678
    verified: 2026-03-19
```

**`rel` type vocabulary:**

| rel type | Meaning | Reference system |
|----------|---------|-----------------|
| `linked` | Informational cross-reference (default) | artifact-refs |
| `documents` | Content dependency, commit-pinned | artifact-refs |
| `aligned` | Alignment decision recorded | artifact-refs |

**`rel-path`** — optional navigable relative path from the referencing artifact to the referenced artifact's file on disk. Populated by the agent when documenting links (e.g., during artifact creation or when adding `artifact-refs` entries). SPEC-103's staleness tooling checks `rel-path` values like any other artifact path — flagging broken ones and updating them via relink when artifacts move between phase directories.

`sourcecode-refs` entries implicitly carry a `describes` relationship — no explicit `rel` field needed.

**Unchanged:** `linked-artifacts` (v1 flat list), `superseded-by`, `depends-on-artifacts` remain as standalone fields.

## Acceptance Criteria

- **Given** a TRAIN definition references enriched `linked-artifacts`, **When** the rename is applied, **Then** it uses `artifact-refs` with identical structure and semantics
- **Given** a DESIGN artifact has `sourcecode-refs` entries, **When** frontmatter is parsed, **Then** each entry has `path`, `blob`, `commit`, and `verified` fields
- **Given** an `artifact-refs` entry, **When** `rel` is omitted, **Then** it defaults to `[linked]`
- **Given** an `artifact-refs` entry, **When** `rel-path` is present, **Then** it is a relative path from the referencing file to the referenced artifact that resolves to an existing file
- **Given** the TRAIN template, **When** updated, **Then** it uses `artifact-refs` instead of enriched `linked-artifacts`
- **Given** the DESIGN template, **When** updated, **Then** it includes both `artifact-refs` and `sourcecode-refs` fields
- **Given** the relationship model, **When** updated, **Then** it reflects EPIC→DESIGN `aligned` edges and the `rel` vocabulary

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Update TRAIN definition, template, and `train-check.sh` to read `artifact-refs` instead of enriched `linked-artifacts`
- Update DESIGN definition and template to include both new fields
- Update relationship model (`references/relationship-model.md`)
- Update `extract_list_ids` and any frontmatter parsers in specwatch/specgraph that read enriched `linked-artifacts`
- At implementation time, scan for any existing TRAIN artifacts with enriched entries and migrate them

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Created from EPIC-035 decomposition |
