---
title: "Retro: Session roadmap infrastructure sprint"
artifact: RETRO-2026-03-22-session-roadmap-infrastructure
track: standing
status: Active
created: 2026-03-22
last-updated: 2026-03-22
scope: "SPEC-170, SPEC-143, SPEC-118 implementation + SPEC-147 renumber"
period: "2026-03-22 — 2026-03-22"
linked-artifacts:
  - SPEC-170
  - SPEC-140
  - SPEC-143
  - SPEC-118
  - SPEC-147
  - EPIC-039
  - INITIATIVE-019
---

# Retro: Session roadmap infrastructure sprint

## Summary

Single-session sprint shipping three specs across the roadmap and session infrastructure. SPEC-170 (Decisions + Recommendation sections in ROADMAP.md) was implemented from scratch with TDD. SPEC-143 (per-artifact roadmap slices) was discovered already implemented on an unmerged worktree branch — retroactively verified and merged with conflict resolution. SPEC-118 (SESSION-ROADMAP.md) was implemented after resolving design questions with the operator, introducing a JSONL decision log as durable storage.

Also fixed an artifact ID collision (SPEC-118 duplicated) by renumbering the trunk helper to SPEC-147, and cleaned up 15 stale worktrees + 27 orphaned branches.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-170 | ROADMAP.md Decision and Recommendation Sections | Complete (13 new tests) |
| SPEC-143 | Per-Vision and Per-Initiative Roadmap Slices | Complete (retroactive close, 15 tests on branch) |
| SPEC-118 | SESSION-ROADMAP.md Format and Generation | Complete (17 new tests) |
| SPEC-147 | swain_trunk() Auto-Detection Helper | Renumbered from SPEC-118 (collision fix) |

## Reflection

### What went well

- **Retroactive close path worked.** SPEC-143 had 8 commits on an unmerged branch. Detection via `git log --all`, test verification on the branch, and merge with conflict resolution was clean and fast — avoided re-implementing already-done work.
- **Design decisions before implementation.** SPEC-118 required 4 operator decisions (session goal interaction model, decision log format, walk-away authorship, progress diff source). Surfacing these upfront prevented mid-implementation pivots.
- **JSONL + rendered markdown.** The operator's insight that decision records should be durable (JSONL) but rendered in SESSION-ROADMAP.md on generation was the right call — it cleanly separates the append-only log from the regenerated surface.
- **Parallel task tracking.** Claiming independent RED tasks (tests for session_roadmap + tests for session_decisions) simultaneously then implementing both kept velocity high.

### What was surprising

- **SPEC-118 ID collision.** Two different specs shared the same artifact ID. The collision was invisible until implementation started — `find` returned two files. Creation-date forensics (git log --diff-filter=A) resolved which was first. This validates that SPEC-140 (Artifact ID Collision Detection) is a real need, not theoretical.
- **chart_cli.py didn't pass edges.** SPEC-170's integration test caught that `render_roadmap_markdown` was called without `edges`, causing the new sections to produce empty output despite unit tests passing. Same pattern noted in prior retros — unit fixtures don't catch wiring bugs.

### What would change

- **Check for unmerged worktree branches before starting implementation.** The SPEC-143 retroactive close was efficient, but discovering it mid-plan-creation was disruptive. A pre-implementation step of `git log --oneline --all | grep SPEC-NNN` (which swain-do already prescribes) caught it — but checking for unmerged *branches* specifically would be more direct.

### Patterns observed

- **Integration test on real data is non-negotiable.** This is the third session where unit tests pass but real-data integration reveals wiring issues (missing parameters, empty outputs). The pattern is consistent enough to be a rule.
- **Worktree accumulation is a housekeeping tax.** 15 stale worktrees from prior sessions, some with uncommitted changes. The doctor check flags them but doesn't auto-clean. Manual cleanup took ~2 minutes but required judgment calls on dirty worktrees.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| (none created) | — | No new behavioral patterns beyond what's already captured. Integration testing pattern is well-established. |
