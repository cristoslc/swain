---
title: "Doctor Python Migration"
artifact: SPIKE-062
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "Should swain-doctor be rewritten in Python, executed via uv?"
gate: Post-SPEC-288
parent-epic: EPIC-068
risks-addressed:
  - Bash at 1,100+ lines is fragile — quoting, portability, error handling are all harder than in Python.
  - Python has native JSON handling, pathlib, and subprocess — all heavily used by doctor checks.
  - uv is already a required dependency, so the runtime cost is zero.
---

# Doctor Python Migration

## Summary

## Question

Should swain-doctor be rewritten in Python, executed via `uv run`?

## Go / No-Go Criteria

- **Go**: a Python prototype reproduces identical JSON output for the same project state, runs in under 3 seconds (matching bash performance), and the migration path is clear (no bash-only features that resist porting).
- **No-Go**: Python adds startup latency above 3 seconds, or critical checks depend on bash-specific features (e.g., sourcing library scripts, process substitution patterns) that make porting impractical.

## Pivot Recommendation

If No-Go, keep bash and apply findings from SPIKE-061 (simplification) instead. A hybrid approach (Python orchestrator shelling out to bash helpers) is also worth evaluating.

## Findings

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | _pending_ | Blocked on SPEC-288 completion (needs stable baseline). |
