---
title: "Fix Duplicate SPIKE IDs Blocking Artifact Graph"
artifact: SPEC-308
track: implementable
status: Complete
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
priority-weight: high
type: bug
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Fix Duplicate SPIKE IDs Blocking Artifact Graph

## Problem Statement

`chart.sh` crashes with a `ValueError: Duplicate artifact IDs detected` error,
blocking all graph-dependent operations: `chart.sh scope`, `chart.sh unanchored`,
`specwatch.sh scan`, and swain-roadmap generation. The crash comes from two causes.

**Cause 1 — Partial migration.** Six SPIKEs were copied to `docs/research/` during
a migration from the legacy `docs/spike/` directory, but the originals in `docs/spike/`
were not removed. Both copies share the same `artifact:` ID:

| ID | Legacy path (docs/spike/) | Migrated path (docs/research/) |
|----|--------------------------|-------------------------------|
| SPIKE-052 | Active/ | Proposed/ |
| SPIKE-058 | Proposed/ | Active/ |
| SPIKE-059 | Complete/ | Complete/ |
| SPIKE-060 | Complete/ | Proposed/ |
| SPIKE-061 | Active/ | Active/ |
| SPIKE-062 | Active/ | Active/ |

**Cause 2 — Filename/frontmatter mismatch.** The folder
`docs/research/Complete/(SPIKE-069)-Trafilatura-Content-Extraction/`
has `artifact: SPIKE-071` in its frontmatter. This collides with
`docs/research/Complete/(SPIKE-071)-ADR-041-Migration-Scope/`, which also declares
`artifact: SPIKE-071`. The trafilatura folder was renamed during an earlier renumbering
but its folder name was never updated.

Eight additional SPIKEs remain only in `docs/spike/` (053, 056, 057, 064, 065, 066, 067, 068).
These do not cause graph crashes today, but they are unreachable by any graph tool and
outside the canonical `docs/research/` location.

## Desired Outcomes

`chart.sh` runs without errors. All duplicate-ID crashes are eliminated. SPIKEs
live under `docs/research/` only. The trafilatura spike has a consistent ID across
folder name and frontmatter.

## External Behavior

- `bash .agents/bin/chart.sh scope SPIKE-069` returns a result without crashing.
- `bash .agents/bin/chart.sh unanchored` returns a result without crashing.
- `bash .agents/bin/specwatch.sh scan` completes without a duplicate-ID error.
- No SPIKE artifact has more than one copy in the repo.
- `docs/spike/` is empty or removed.

## Acceptance Criteria

- **AC1:** Running `chart.sh scope SPIKE-069` exits 0 and shows the ancestry chain.
- **AC2:** Running `chart.sh unanchored` exits 0 with no `ValueError`.
- **AC3:** `grep -r "^artifact:" docs/spike/ 2>/dev/null` returns no output (legacy dir is empty or absent).
- **AC4:** Exactly one file in `docs/research/` declares `artifact: SPIKE-071`. Its folder name matches its ID.
- **AC5:** The six migrated SPIKEs (052, 058, 059, 060, 061, 062) have exactly one copy each, in `docs/research/`.
- **AC6:** The eight unmigrated SPIKEs (053, 056, 057, 064, 065, 066, 067, 068) have been moved to `docs/research/` in the correct phase subdirectory, matching their frontmatter `status:` field.

## Reproduction Steps

```bash
bash .agents/bin/chart.sh scope SPIKE-069
```

**Output:**
```
ValueError: Duplicate artifact IDs detected: SPIKE-052: ...; SPIKE-058: ...; ...
```

## Severity

high — blocks all graph-dependent operations including roadmap generation and
specwatch, making the artifact system partially blind.

## Expected vs. Actual Behavior

**Expected:** `chart.sh` builds a graph from `docs/research/` only and returns
ancestry chains without error.

**Actual:** `chart.sh` scans all `docs/` subdirectories, finds the same artifact IDs
in both `docs/spike/` and `docs/research/`, and raises a duplicate-ID error before
any query can execute.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| AC1 | `chart.sh scope SPIKE-069` exits 0 | PASS: scope SPIKE-072 returns ancestry chain |
| AC2 | `chart.sh unanchored` exits 0 | PASS: no ValueError |
| AC3 | no artifact frontmatter in docs/spike/ | PASS: directory removed |
| AC4 | one SPIKE-071 file, folder name matches | PASS: (SPIKE-071)-ADR-041-Migration-Scope |
| AC5 | six migrated IDs have one copy each | PASS: all six in docs/research/ only |
| AC6 | eight legacy-only IDs present in docs/research/ | PASS: all eight migrated to correct phase dirs |

## Scope & Constraints

In scope: remove duplicate copies, migrate legacy-only SPIKEs, fix the
trafilatura folder name.

Out of scope: content edits to any SPIKE, phase transitions, ADR or link updates
unrelated to the ID collision. Do not alter any SPIKE's phase or content during
the move — only fix location and folder naming.

## Implementation Approach

1. **Fix Cause 2 first** (trafilatura mismatch). Determine the correct ID. The
   folder says `SPIKE-069` (the original number) but frontmatter says `SPIKE-071`.
   Check whether `SPIKE-069` is already taken in `docs/research/` — it is (this
   SPIKE's parent research). So the trafilatura spike needs its own clean ID.
   Assign the next available ID above the current max (run `next-artifact-id.sh SPIKE`
   at fix time). Rename folder and update frontmatter in one `git mv` + edit.

2. **Remove stale copies from docs/spike/** for the six migrated SPIKEs. For each,
   confirm the `docs/research/` copy is the canonical one (has all content), then
   `git rm -r` the `docs/spike/` copy.

3. **Migrate legacy-only SPIKEs** (053, 056, 057, 064, 065, 066, 067, 068) to
   `docs/research/<phase>/` matching each spike's frontmatter `status:` field. Use
   `git mv` to preserve history.

4. **Remove `docs/spike/`** once empty.

5. Run `chart.sh scope SPIKE-069` and `chart.sh unanchored` to confirm no errors.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-14 | — | Identified during SPIKE-069 creation; chart.sh scope blocked |
| Complete | 2026-04-14 | — | Resolved: removed docs/spike/ duplicates, migrated 8 legacy SPIKEs, renamed trafilatura to SPIKE-072 |
