---
title: "Normalize Artifact Frontmatter Relationships"
artifact: SPEC-009
status: Draft
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
type: feature
parent-epic: ""
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
linked-artifacts: []
depends-on-artifacts: []
---

# Normalize Artifact Frontmatter Relationships

## Problem Statement

Artifact frontmatter uses inconsistent, per-type link fields (`linked-research`, `linked-adrs`, `linked-epics`, `linked-specs`) alongside a generic `depends-on` field. This creates two problems:

1. **Wrong semantics for spikes.** Spikes have `depends-on` in their template but it is always empty — spikes are purely investigative and have no blocking dependencies, only informational relationships. The field implies a blocking dependency that does not exist, which confuses specgraph and human readers alike.

2. **Fragmented link schema.** Each artifact type invents its own typed link fields. There is no uniform way for tooling (specgraph, specwatch) to enumerate all cross-references without knowing each type's specific field names.

This was first reported by a consumer noticing incorrect dependency directions in the artifact graph.

## External Behavior

After this spec is implemented:

- All informational cross-references (previously `linked-research`, `linked-adrs`, `linked-epics`, `linked-specs`) are expressed as a single `linked-artifacts` list in frontmatter.
- All blocking dependencies (previously `depends-on`) are expressed as `depends-on-artifacts`.
- Spike artifacts have `linked-artifacts` only — no `depends-on-artifacts` field.
- specgraph reads `linked-artifacts` for graph edges and `depends-on-artifacts` for blocking edges.
- specwatch validates that referenced artifact IDs in both fields exist on disk.
- Existing artifact files are migrated to the new field names.

## Acceptance Criteria

- **Given** any artifact template, **when** a new artifact is created, **then** its frontmatter contains `linked-artifacts` (not per-type variants) and `depends-on-artifacts` (not `depends-on`).
- **Given** the spike template, **when** a new spike is created, **then** its frontmatter contains `linked-artifacts` and does NOT contain `depends-on-artifacts`.
- **Given** an existing artifact with `linked-research`, `linked-adrs`, `linked-epics`, or `linked-specs`, **when** specwatch scans, **then** it reports those as stale field names.
- **Given** specgraph runs `edges` or `blocks` on any artifact, **when** it reads relationships, **then** it reads from `linked-artifacts` and `depends-on-artifacts` (not the old per-type fields).
- **Given** all existing artifact files in `docs/`, **when** the migration script runs, **then** all old field names are replaced with the normalized names and no artifact data is lost.

## Scope & Constraints

In scope:
- Templates: spike, spec, adr, epic (and any others with `linked-*` or `depends-on` fields)
- Existing artifact files under `docs/`
- specgraph.sh (field name reads)
- specwatch.sh (field name validation)
- A migration script to update existing files

Out of scope:
- Changing the meaning of relationships (blocking vs. informational) — only renaming fields
- Adding new relationship types

## Implementation Approach

1. Audit all templates and existing artifact files to enumerate field names in use.
2. Write a migration script that renames fields in-place across all `docs/**/*.md` files.
3. Update each template file.
4. Update specgraph.sh field references.
5. Update specwatch.sh validation rules.
6. Run the migration script, verify no data loss, commit.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-13 | — | Initial creation |
