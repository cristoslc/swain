---
title: "Retro: SPEC-214 Operator Bin Symlink Auto-Repair"
artifact: RETRO-2026-03-31-spec-214-operator-bin-auto-repair
track: standing
status: Active
created: 2026-03-31
last-updated: 2026-03-31
scope: "SPEC-214 — auto-repair of bin/ operator symlinks in consumer projects"
period: "2026-03-31 — 2026-03-31"
linked-artifacts:
  - SPEC-214
  - EPIC-046
  - SPEC-180
  - SPEC-181
  - ADR-019
---

# Retro: SPEC-214 Operator Bin Symlink Auto-Repair

## Summary

Identified and fixed a gap where `bin/swain` and `bin/swain-box` were never auto-created in consumer projects after `swain-update`. Doctor checks 15 and 19 warned but never repaired. Introduced a `skills/swain/usr/bin/` manifest directory as a single source of truth for operator-facing scripts, consolidated two warn-only checks into one scan-and-repair check, and updated swain-init. 20/20 new tests, 11/11 existing tests passing.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-214 | Operator Bin Symlink Auto-Repair | Complete |

## Reflection

### What went well

**Operator design instinct was right.** The `skills/swain/usr/bin/` manifest idea came from the operator mid-conversation ("maybe we need a folder for scripts that doctor and init can check against canonically?"). It solved two problems at once: auto-repair and the hardcoded exclusion list in Check 20. The architectural insight was better than the initial fix-in-place approach would have been.

**Test coverage was thorough.** All 7 ACs mapped directly to test cases. The test for AC5 (new script gets symlink without code changes) validated the manifest pattern's extensibility claim rather than just current behavior.

**Merge resolution preserved both sets of improvements.** The push conflicted with trunk's enhanced Check 20 auto-repair logic (stale symlink detection, `mkdir -p`, broken link cleanup). The resolved version combined both — dynamic exclusion from SPEC-214 plus trunk's auto-repair improvements — without losing either.

### What was surprising

**The SPEC was created on trunk before the worktree was entered.** The diagnosis and spec creation happened in the main checkout, then the worktree was opened for implementation. This left a stale untracked directory on trunk (`docs/spec/Active/(SPEC-214)...`) that required manual cleanup after the worktree was removed. A small violation of worktree isolation that cost an extra cleanup step.

**Smoke tests weren't run proactively.** After 20/20 unit tests passed, the work was presented as ready to push. The operator had to ask "did you run smoke tests?" before the full doctor was run. The full run was clean, but the ask should not have been necessary — smoke testing the full script is obvious after modifying its check functions.

### What would change

Run the full doctor (`bash .agents/bin/swain-doctor.sh`) as a standard step after modifying `swain-doctor.sh`, before reporting completion. Unit tests and smoke tests serve different purposes — unit tests check specific logic; smoke test checks the full check function composition.

### Patterns observed

**Warn-only checks are traps.** Checks 15 and 19 were written as detection-only but sat adjacent to a check (Check 20) that auto-repairs. The asymmetry is invisible until a consumer project fails silently. Every doctor check that can auto-repair safely should auto-repair — warn-only is only appropriate when repair is destructive or ambiguous.

**Hardcoded exclusion lists are a sign of missing abstraction.** The `operator_scripts="swain swain-box"` string in Check 20 was a smell from the start. It required edits in two places to add a new script. The manifest directory makes the list self-maintaining.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Doctor: smoke-test full script after modifying checks | SPEC candidate | Add smoke test step to implementation workflow for swain-doctor changes |
| SPEC creation should happen inside the worktree | SPEC candidate | Detect when SPEC artifact is created on trunk before worktree entry; warn or defer |
| Warn-only doctor checks audit | SPEC candidate | Audit all remaining warn-only checks for safe auto-repair candidates |

## SPEC candidates

1. **Doctor smoke-test gate** — When implementing changes to `swain-doctor.sh`, the implementation workflow (swain-do TDD cycle) should include an explicit step to run the full doctor as a smoke test after unit tests pass. Currently, this is skipped unless the operator asks. Should be part of the standard "verification before completion" gate for doctor changes specifically.

2. **SPEC artifact created before worktree entry** — SPEC-214 was created in the main checkout, then the worktree was entered for implementation. The worktree isolation rule says "all file-mutating work happens in a worktree" but artifact creation before the worktree is a natural flow (diagnose → spec → implement). Consider whether swain-design should detect this and offer to defer artifact writing until a worktree is entered, or whether the cleanup step should be automated in swain-do's worktree preamble.

3. **Warn-only doctor check audit** — With Check 20's auto-repair pattern now well-established and SPEC-214 extending it to operator scripts, audit the remaining warn-only checks for safe promotion to auto-repair. Candidates: commit signing (could set it), governance block freshness (could update it), crash debris (some debris types are safe to auto-clean).
