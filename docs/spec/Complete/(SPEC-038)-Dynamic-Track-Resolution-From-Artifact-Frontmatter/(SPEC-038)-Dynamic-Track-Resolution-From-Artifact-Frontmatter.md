---
title: "SPEC-038: Dynamic Track Resolution from Artifact Frontmatter"
artifact: SPEC-038
track: implementable
status: Complete
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
type: feature
parent-epic: EPIC-013
linked-artifacts:
  - ADR-003
  - SPEC-037
depends-on-artifacts: []
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# Dynamic Track Resolution from Artifact Frontmatter

## Problem Statement

Specgraph hardcodes artifact resolution logic — a `RESOLVED_RE` regex and a type-matching `is_resolved` jq helper that lists standing-track types by name. This duplicates knowledge from ADR-003 (three lifecycle tracks) and drifts when artifact types change. SPEC-037 was a direct consequence: `do_ready` had a stale copy of the resolution logic.

The fix is to make artifacts self-defining via their track membership, with a single tracks index that defines what each track's phases and terminal semantics are. Specgraph derives resolution dynamically from these two inputs instead of maintaining its own parallel list.

## Design

### Tracks index

A single file (`references/lifecycle-tracks.md` or `.yaml`) defines the three tracks from ADR-003:

| Track | Phases (ordered) | Terminal phases | Resolution rule |
|-------|-----------------|-----------------|-----------------|
| implementable | Proposed → Ready → In Progress → Needs Manual Test → Complete | Complete | Status is terminal |
| container | Proposed → Active → Complete | Complete | Status is terminal |
| standing | Proposed → Active → (Retired \| Superseded) | Retired, Superseded | Active OR status is terminal |

Universal terminal states (Abandoned, Retired, Superseded) apply to all tracks.

### Artifact definitions

Each artifact definition file gains a required `track` field:

- SPEC: `track: implementable`
- EPIC, SPIKE: `track: container`
- VISION, JOURNEY, PERSONA, ADR, RUNBOOK, DESIGN: `track: standing`

### Artifact templates

Templates propagate `track` into the frontmatter of new artifacts so specgraph can read it per-node at build time.

### Specgraph

At `do_build` time, specgraph reads each artifact's `track` field from frontmatter. The `is_resolved` logic looks up that track's resolution rule from the tracks index instead of pattern-matching on type names.

The hardcoded `RESOLVED_RE` and type-matching `is_resolved` helpers are removed entirely.

### Design audit

The audit's **Naming & structure validator** agent gains an additional check: every artifact must have a `track` field, and it must be one of the values defined in the tracks index. Missing or invalid `track` fields are flagged as errors.

## External Behavior

- **Specgraph output is unchanged** — same ready/next/overview/status results, but derived dynamically
- **New artifact types** only need to declare `track: <track-name>` — no specgraph code changes required
- **Audit** flags artifacts missing the `track` field

## Acceptance Criteria

- Given a tracks index file defining three tracks with their terminal phases, specgraph reads it at build time
- Given an artifact with `track: standing` and `status: Active`, specgraph treats it as resolved
- Given an artifact with `track: implementable` and `status: Active`, specgraph treats it as unresolved
- Given an artifact missing a `track` field, specgraph emits a warning during build and falls back to type-based inference (migration compat)
- Given an artifact missing a `track` field, the design audit flags it as an error
- Given a new artifact type added with `track: container`, specgraph handles it without code changes
- `specgraph.sh ready` output matches the Ready section of `specgraph.sh overview` (regression gate from SPEC-037)

## Scope & Constraints

- The tracks index is a reference file, not runtime config — it changes only when ADR-003 is superseded
- Existing artifacts without `track` fields must degrade gracefully (warn + infer from type) during migration
- This SPEC does not change the track definitions themselves — those are governed by ADR-003
- Applies to both the bash specgraph and the Python rewrite (EPIC-013)

## Implementation Approach

1. Create the tracks index file with the three tracks from ADR-003
2. Add `track` field to all 9 artifact definition files
3. Add `track` field to all 9 artifact templates
4. Update specgraph `do_build` to extract `track` from each artifact's frontmatter
5. Replace `RESOLVED_RE` and hardcoded `is_resolved` with dynamic track-based lookup
6. Add fallback: if `track` is missing, infer from type name and warn
7. Add `track` validation to the audit's naming & structure validator
8. Backfill `track` into all existing artifacts (migration script or specwatch fix)
9. Verify `ready`/`next`/`overview` output is identical before and after

## Verification

| Acceptance Criterion | Evidence | Result |
|----------------------|----------|--------|
| Tracks index file exists; specgraph reads `track` at build time | `lifecycle-tracks.md` created; `specgraph.sh build` extracts `track` from frontmatter with `get_field "$file" "track"` | Pass |
| `track: standing` + `status: Active` → resolved | ADRs (e.g., ADR-001 Active) absent from `specgraph.sh ready` output | Pass |
| `track: implementable` + `status: Active` → unresolved | SPEC-031 (Active) appears in `specgraph.sh ready` output | Pass |
| Missing `track` → TRACK_MISSING warning + type-based inference | `bash specgraph.sh build 2>&1 \| grep TRACK_MISSING` = 87 warnings before backfill, 0 after | Pass |
| Missing `track` → design audit error | `auditing.md` Naming & structure validator updated to flag missing/invalid `track` as error | Pass |
| New type with `track: container` → works without code changes | `is_resolved` now uses `.track == "standing"` instead of type name regex — no hardcoded type list | Pass |
| `specgraph.sh ready` matches overview Ready section | Verified: identical artifact sets in both bash and python ready/overview output | Pass |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | | Initial creation |
| Ready | 2026-03-14 | b4037a0 | Batch approval — ADR compliance and alignment checks pass |
| Complete | 2026-03-14 | 3a42d93 | All 8 ACs verified; 87 artifacts backfilled, 0 TRACK_MISSING warnings |
