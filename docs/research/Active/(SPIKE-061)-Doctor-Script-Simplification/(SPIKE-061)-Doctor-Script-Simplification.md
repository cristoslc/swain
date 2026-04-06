---
title: "Doctor Script Simplification"
artifact: SPIKE-061
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "Can swain-doctor.sh be simplified below 500 lines without losing functionality?"
gate: Post-SPEC-288
parent-epic: EPIC-068
risks-addressed:
  - 1,100+ lines of bash is hard to maintain and audit.
  - Check functions have repeated patterns (detection → add_check) that could be data-driven.
  - Some checks shell out to helper scripts that could absorb their parent check entirely.
---

# Doctor Script Simplification

## Summary

## Question

Can swain-doctor.sh be simplified below 500 lines without losing functionality?

## Go / No-Go Criteria

- **Go**: a refactored script passes all existing checks identically (same JSON output for the same project state) and is under 500 lines.
- **No-Go**: the refactored script cannot reproduce identical output, or the data-driven approach introduces more complexity than it removes.

## Pivot Recommendation

If No-Go, keep the current script and focus on documentation and test coverage instead. Consider SPIKE-062 (Python migration) as an alternative simplification path.

## Findings

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | _pending_ | Blocked on SPEC-288 completion (needs stable baseline). |
