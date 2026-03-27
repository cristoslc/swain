---
title: "design-check.sh — Blob SHA Drift Detection"
artifact: SPEC-096
track: implementable
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
type: ""
parent-epic: EPIC-035
parent-initiative: ""
linked-artifacts:
  - SPEC-094
  - SPEC-097
depends-on-artifacts:
  - SPEC-094
addresses: []
trove: ""
source-issue: ""
swain-do: required
---

# design-check.sh — Blob SHA Drift Detection

## Problem Statement

DESIGN artifacts need automated drift detection against implementation source files. Unlike TRAIN's commit-based staleness (comparing artifact commits), DESIGN drift requires file-level tracking with blob SHA pinning to survive renames and refactors.

## External Behavior

New script `skills/swain-design/scripts/design-check.sh`, sister to `train-check.sh`.

**Input:** Path to a single DESIGN artifact, or no argument to scan all active DESIGNs under `docs/design/`.

**Reads:** `sourcecode-refs` entries from DESIGN frontmatter (requires SPEC-094 schema).

**Algorithm per entry:**

1. Path exists at HEAD? Compare current blob SHA vs pinned:
   - Same → **CURRENT**
   - Different → **STALE**
2. Path missing at HEAD? Search HEAD tree for pinned blob SHA (`git ls-tree -r HEAD | grep <blob>`):
   - Found at new path → **MOVED**
   - Not found → `git diff --find-renames --diff-filter=R <pinned-commit> HEAD -- <original-path>`:
     - Rename found → **MOVED+STALE**
     - No rename → **BROKEN**

**Getting blob SHA at pin time:** `git ls-tree HEAD -- <path> | awk '{print $3}'`

**Exit codes:**
- 0 = all refs CURRENT or MOVED (content intact)
- 1 = at least one ref is STALE, MOVED+STALE, or BROKEN
- 2 = git unavailable (graceful degradation)

**Output format:** One line per entry: `<status> <path> [→ <new-path>] [<commits-behind>]`

**Re-pin mode:** `design-check.sh --repin <design-path>` updates all `sourcecode-refs` entries to current blob SHA and commit. Operator confirms before write.

## Acceptance Criteria

- **Given** a DESIGN with `sourcecode-refs` pointing to unchanged files, **When** `design-check.sh` runs, **Then** exit 0 and report all CURRENT
- **Given** a `sourcecode-refs` entry whose file was modified since pinned commit, **When** `design-check.sh` runs, **Then** report STALE with commits-behind count, exit 1
- **Given** a `sourcecode-refs` entry whose file was renamed (same content), **When** `design-check.sh` runs, **Then** report MOVED with old→new path, exit 0
- **Given** a `sourcecode-refs` entry whose file was renamed AND modified, **When** `design-check.sh` runs, **Then** report MOVED+STALE, exit 1
- **Given** a `sourcecode-refs` entry whose file was deleted with no rename target, **When** `design-check.sh` runs, **Then** report BROKEN, exit 1
- **Given** no argument, **When** `design-check.sh` runs, **Then** scan all active DESIGNs under `docs/design/Active/`
- **Given** `--repin` flag, **When** run, **Then** update blob SHA and commit in frontmatter for all entries
- **Given** git is unavailable, **When** `design-check.sh` runs, **Then** exit 2

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Script must be POSIX-compatible (bash, no Python dependency for the core check)
- Blob SHA lookup via `git ls-tree -r HEAD` is O(n) over file tree — acceptable for typical `sourcecode-refs` counts (<20 entries per DESIGN)
- Does not auto-update paths on MOVED — reports only; operator decides
- `--repin` writes to frontmatter but does not commit

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | -- | Created from EPIC-035 decomposition |
