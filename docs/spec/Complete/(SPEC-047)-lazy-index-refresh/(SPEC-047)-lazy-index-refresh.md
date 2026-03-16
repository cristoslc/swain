---
title: "Lazy Index Refresh for list-*.md Artifact Indices"
artifact: SPEC-047
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: enhancement
parent-epic: EPIC-014
linked-artifacts:
  - EPIC-014
depends-on-artifacts:
  - SPIKE-018
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Lazy Index Refresh for list-*.md Artifact Indices

## Problem Statement

swain-design updates `list-<type>.md` index files as part of every artifact creation and phase transition (~600 tokens, 2 tool calls per artifact). SPIKE-018 found these indices duplicate information already in frontmatter and add no query acceleration — `specgraph.py build` rebuilds from frontmatter in 116ms. The index is a human-facing display artifact, not a query substrate. For sessions that create multiple artifacts, the per-artifact index update is redundant overhead.

## External Behavior

The `list-<type>.md` index is refreshed lazily rather than per-artifact:

- **Trigger**: Index refresh runs when (a) explicitly requested by the user, (b) `specgraph.sh build --force` is invoked, or (c) swain-session or swain-sync runs at the end of a session
- **Per-artifact creation/transition**: Index update is skipped; only frontmatter is written
- **Batch refresh**: `skills/swain-design/scripts/rebuild-index.sh <type>` (new script) scans all artifacts of a given type across all phase directories and regenerates `list-<type>.md` from frontmatter

The index schema is unchanged. The batch refresh is idempotent (safe to run multiple times). swain-sync already runs at session end; it gains a call to `rebuild-index.sh` for any type that had artifact activity in the session.

## Acceptance Criteria

1. **Given** a new artifact is created, **when** swain-design runs, **then** `list-<type>.md` is NOT updated as part of the creation workflow
2. **Given** a phase transition occurs, **when** swain-design runs, **then** `list-<type>.md` is NOT updated as part of the transition workflow
3. **Given** `rebuild-index.sh spec` is run, **when** it completes, **then** `list-spec.md` reflects all current SPECs with correct status, date, and commit hash columns
4. **Given** swain-sync runs at session end, **when** any SPEC/EPIC/SPIKE was created or transitioned in the session, **then** `rebuild-index.sh` is called for each affected type before committing
5. **Given** the index is stale (artifact created but index not yet refreshed), **when** a user reads `list-<type>.md`, **then** the staleness is not visible to specgraph (it reads frontmatter, not the index), only to direct human readers of the file

## Scope & Constraints

**In scope:**
- Creating `skills/swain-design/scripts/rebuild-index.sh` — scan all artifacts, regenerate index
- Updating swain-design SKILL.md §Index refresh step to be conditional (skip per-artifact, batch at session end)
- Updating `skills/swain-design/references/index-maintenance.md` with lazy refresh semantics
- Updating swain-sync SKILL.md to invoke `rebuild-index.sh` for affected types

**Out of scope:**
- Changing the `list-<type>.md` schema or column format
- Making `specgraph.py` read from the index (it already reads frontmatter — no change)
- Eager per-artifact index update (the per-artifact path is removed, not optional)

## Implementation Approach

1. Write `skills/swain-design/scripts/rebuild-index.sh`:
   - Accept artifact type as argument (`spec`, `epic`, `spike`, `adr`, etc.)
   - `find docs/<type>/ -name '*.md'` across all phase subdirectories
   - Extract `artifact:`, `title:`, `last-updated:`, and latest lifecycle commit from each
   - Group by phase (Proposed/Ready/Active/Complete/etc.) and write table sections
   - Atomic write via temp file → rename
2. Update SKILL.md workflow step 10 to call `rebuild-index.sh` only at session-end trigger
3. Update swain-sync to detect session artifact activity and call `rebuild-index.sh`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | c0e77ed | Initial creation from SPIKE-018 GO decision |
| Ready | 2026-03-14 | c0e77ed | Approved — lazy index refresh complements fast-path and inline stamp |
| Complete | 2026-03-14 | b4892cd | Fast-path tier detection and lazy index rebuild.sh implemented; swain-design SKILL.md updated |
