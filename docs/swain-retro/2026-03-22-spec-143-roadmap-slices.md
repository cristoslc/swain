---
title: "Retro: SPEC-143 Per-Vision and Per-Initiative Roadmap Slices"
artifact: RETRO-2026-03-22-spec-143-roadmap-slices
track: standing
status: Active
created: 2026-03-22
last-updated: 2026-03-22
scope: "SPEC-143 implementation — scoped roadmap slices for Visions and Initiatives"
period: "2026-03-21 — 2026-03-22"
linked-artifacts:
  - SPEC-143
  - SPEC-144
---

# Retro: SPEC-143 Per-Vision and Per-Initiative Roadmap Slices

## Summary

Implemented `chart.sh roadmap --scope <ID>` for per-Vision and per-Initiative roadmap slices. Replaced the existing `--focus` flag. Project-wide `chart.sh roadmap` now regenerates all 23 slices alongside ROADMAP.md. Created SPEC-144 (brief-description frontmatter field) as a companion spec for intent resolution.

17 commits total: 8 feature commits landed via parallel subagents, then 5 fix/polish commits emerged from operator-driven manual testing. 11/11 tk tasks closed. 75/75 unit tests pass throughout.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-143](../spec/Complete/(SPEC-143)-Per-Vision-Per-Initiative-Roadmap-Slices/(SPEC-143)-Per-Vision-Per-Initiative-Roadmap-Slices.md) | Per-Vision and Per-Initiative Roadmap Slices | Complete |
| [SPEC-144](../spec/Active/(SPEC-144)-Brief-Description-Frontmatter-Field/(SPEC-144)-Brief-Description-Frontmatter-Field.md) | Brief Description Frontmatter Field | Created (not yet implemented) |

## Reflection

### What went well

- **Parallel subagent execution** worked cleanly for the first batch (T1, T2, T4 — graph.py, _compute_descendants, Jinja template). Three independent tasks completed in background while doc tasks (T8, T9) were done in the main thread. No merge conflicts between agents.
- **Issue-to-SPEC-to-plan pipeline** was smooth: GitHub Issue #84 → SPEC-143 → brainstorming → design doc → implementation plan → tk tasks → execution. The full chain fired without manual intervention.
- **Operator manual test walkthrough** caught 5 issues the automated tests missed — all UX/presentation concerns that unit tests can't cover (sort order, tree vs flat table, progress counting semantics, timestamp format).

### What was surprising

- **Progress counting has non-obvious semantics.** Three different counting strategies were tried: SPEC-leaf counting (wrong — invisible childless Epics), direct-children-only (confusing — tree shows grandchildren but counter doesn't), and all-descendants (correct — matches what the operator sees). The "right" answer was the one that matched visual expectation, not the one that was architecturally cleanest.
- **The `--focus` flag already existed** and did Vision-level filtering, but wrote to the project root with the full template. Discovering this during brainstorming saved a potential conflict. The codebase exploration agent earned its cost here.
- **Five polish commits after "done"** — nearly a third of the commit count came from manual testing. The initial implementation was functionally correct but the presentation needed iteration that only human eyes could drive.

### What would change

- **Run the manual test walkthrough earlier.** The automated tests validated data correctness but all 5 post-implementation fixes were presentation issues (sort order, tree format, grouping, progress semantics, timestamps). Showing the operator a rendered slice after Task 5 instead of after Task 11 would have caught these sooner and avoided rework in later tasks.
- **The children tree format should have been in the spec.** The SPEC described a "child artifact table" — a flat table. The operator wanted a tree grouped by lifecycle phase. This was a design gap that only surfaced during review. Future specs for rendered output should include a mockup.

### Patterns observed

- **Operator review of rendered markdown in Typora** is the quality gate for presentation-layer work. Unit tests catch logic bugs; human review catches UX bugs. This is a recurring pattern — automated tests are necessary but insufficient for output formatting.
- **Generated artifacts need careful progress semantics.** Any time a progress counter appears alongside a tree/list, the counter must count the same things the user sees. Mixing abstraction levels (counting SPECs but showing Epics) creates confusion. This applies beyond roadmap slices.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_manual_test_typora.md | feedback | Open markdown files in Typora for operator review during manual test gates |
