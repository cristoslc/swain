# Retro: SPEC-141 — Spec-Level Priority Weight

**Date:** 2026-03-21
**Scope:** SPEC-141 implementation — standalone spec, no parent epic
**Period:** 2026-03-21 — 2026-03-21

## Summary

Closed a long-standing asymmetry in the priority cascade: Visions, Initiatives, and Epics could all set their own `priority-weight` override, but SPECs could only inherit. The fix was a two-line change in `priority.py` (remove the type whitelist from `resolve_vision_weight`), validated by two new tests, and accompanied by three documentation updates (template, definition, SKILL.md). All 17 tests pass. Shipped in a single session with no scope changes.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-141 | Spec-Level Priority Weight | Complete |

## Reflection

### What went well

The spec was precisely scoped. The implementation approach was fully spelled out in the artifact — the exact before/after code diff, the test function signatures, and the doc locations — which meant there was no discovery work at all. TDD was clean: one failing test, one two-line fix, green. The worktree isolation pattern worked without friction.

### What was surprising

The worktree was branched from the `release` base rather than trunk, so the SPEC-141 artifact itself was absent from the worktree. This required copying the artifact in manually before the phase transition. The worktree base mismatch is a structural issue: `EnterWorktree` branches from whatever HEAD the session started on, which may lag behind trunk.

### What would change

Nothing in the implementation approach. The worktree base mismatch could be avoided by ensuring the worktree is created from trunk rather than the release branch — but this is a session setup concern, not a SPEC concern.

### Patterns observed

A well-specified SPEC collapses implementation time to near zero. When the spec contains the exact code diff, test stubs, and file locations, the agent doesn't need to read extra context or make decisions — it executes. The delta between "spec as behavior contract" and "spec as implementation recipe" is a quality choice the operator makes at authoring time; this SPEC was at the recipe end of that spectrum, which paid off.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| *(none — no novel behavioral findings; worktree base issue tracked in SPEC-142)* | — | — |
