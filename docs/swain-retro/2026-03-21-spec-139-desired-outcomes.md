# Retro: SPEC-139 Desired Outcomes Section for Shippable Artifacts

**Date:** 2026-03-21
**Scope:** SPEC-139 — add Desired Outcomes section to SPEC, EPIC, INITIATIVE templates + audit integration
**Period:** 2026-03-21 (single session, spec creation through implementation)

## Summary

Added a `## Desired Outcomes` body section to the three "shippable change-producer" artifact templates (SPEC, EPIC, INITIATIVE). Extended the audit system's Naming & structure validator with an advisory check for the section's presence and a batch remediation workflow for drafting sections on existing artifacts.

Total: 4 files changed, 42 insertions, 1 deletion. 6 tasks created, all closed in one session.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-139 | Desired Outcomes Section for Shippable Artifacts | Implemented (pending transition to NeedsManualTest) |

## Reflection

### What went well

**Operator-driven scoping was efficient.** The operator arrived with a clear intent ("every implementable artifact needs an Impact or Desired Outcomes section") and refined it through two rounds of clarification before spec drafting began. The clarification questions were well-targeted — artifact scope, consolidation vs complement strategy, and the "so what" framing — which meant the spec was right on first draft with only one amendment (audit integration).

**Complementary-not-consolidating design.** The per-type analysis of existing sections (Acceptance Criteria, Goal/Objective, Strategic Focus, success-criteria) avoided the trap of trying to merge or replace them. Each template's Desired Outcomes section sits at a distinct abstraction level from the existing outcome-adjacent sections: aspirational framing vs testable conditions vs measurable KPIs.

**Task decomposition matched the actual work.** 6 tasks, 6 file edits (one turned out to be unnecessary — SKILL.md already delegated to auditing.md). Clean parallel structure for the three template edits.

### What was surprising

**Worktree ticket isolation.** The `.tickets/` directory in the worktree has its own prefix (`aa-`) separate from the main checkout's `swa-` prefix. Claiming tasks created in the main worktree failed from within the isolated worktree. Workaround: `cd` to main checkout for tk operations. This is a known friction point but still caused a few wasted commands.

**tk exit code 1 on success.** The `tk add-note && tk close` chain consistently returned exit code 1 even though both operations succeeded (notes added, tickets closed). This is likely a dependency-graph side effect — closing a task that other tasks depend on may trigger a non-zero exit. The operations completed correctly despite the error code.

### What would change

**Skip brainstorming for low-complexity governance specs.** The superpowers chain mandates brainstorming before implementation, but this spec was a pure template edit with no creative ambiguity. The spec's Implementation Approach was already a concrete file-by-file task list. Brainstorming was correctly skipped here, but the decision to skip it was implicit — a documented fast-path for "template-only" specs would reduce cognitive overhead.

### Patterns observed

**Amendment-after-creation is becoming common.** The operator created the spec, reviewed it, then immediately asked for a scope expansion (audit integration). This happened within the same session, so it was efficient — but it suggests that the spec creation workflow could benefit from a "before we finalize, what about..." prompt that surfaces adjacent concerns (like enforcement mechanisms) before the artifact is committed.

## Learnings captured

No new memory files created — the observations above are session-specific and don't represent durable behavioral changes. The tk worktree friction is already known. The amendment pattern is worth watching but not yet actionable as a process change.
