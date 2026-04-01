---
title: "Retro: Doctor Artifact Index Repair"
artifact: RETRO-2026-04-01-doctor-artifact-index-repair
track: standing
status: Active
created: 2026-04-01
last-updated: 2026-04-01
scope: "Manual retro for doctor artifact index repair work on SPEC-227"
period: "2026-04-01 — 2026-04-01"
linked-artifacts:
  - SPEC-227
  - SPEC-047
  - SPEC-222
  - INITIATIVE-013
---

# Retro: Doctor Artifact Index Repair

## Summary

This branch closed a gap in `swain-doctor`. Doctor now checks generated artifact index files, repairs stale or missing ones through the existing rebuild path, and reports the repair as advisory work. The change also extended `rebuild-index.sh` and `swain-sync` to cover initiative indices.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-227](../spec/Complete/(SPEC-227)-Doctor-Artifact-Index-Staleness-Repair/(SPEC-227)-Doctor-Artifact-Index-Staleness-Repair.md) | Doctor Artifact Index Staleness Repair | Complete on branch |
| [SPEC-047](../spec/Complete/(SPEC-047)-lazy-index-refresh/(SPEC-047)-lazy-index-refresh.md) | Lazy Index Refresh for list-*.md Artifact Indices | Reused as prior design basis |
| [SPEC-222](../spec/Complete/(SPEC-222)-Doctor-Warn-Only-Check-Auto-Repair-Audit/(SPEC-222)-Doctor-Warn-Only-Check-Auto-Repair-Audit.md) | Doctor Warn-Only Check Auto-Repair Audit | Extended the same repair pattern |
| [INITIATIVE-013](../initiative/Active/(INITIATIVE-013)-Concurrent-Session-Safety/(INITIATIVE-013)-Concurrent-Session-Safety.md) | Concurrent Session Safety | Focus lane for the work |

## Reflection

### What went well

The bug was easy to prove with a live diff from `rebuild-index.sh spec`. That kept the fix small. Reusing the existing rebuild script avoided a second index renderer inside doctor.

### What was surprising

Smoke work exposed real stale repo files outside the feature diff. `docs/initiative/list-initiative.md` was already malformed. The doctor test path could also re-trigger unrelated index and symlink repairs if cleanup was skipped.

### What would change

Future smoke tests for doctor auto-repair paths should run in a tighter fixture or restore wrapper from the start. That would keep the branch diff cleaner and cut cleanup passes before merge.

### Patterns observed

Doctor is becoming the home for safe deterministic repo repair. That pattern is useful, but tests for those repairs need stronger isolation because the happy path mutates real files.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Add isolated fixture coverage for doctor auto-repair smoke paths | SPEC candidate | Verify repair behavior without mutating real repo index files or operator-facing symlinks during branch verification |
