---
title: "Agentrc Primitives Adoption For Swain"
artifact: SPIKE-069
track: container
status: Active
author: cristos
created: 2026-04-14
last-updated: 2026-04-14
parent-initiative: INITIATIVE-016
parent-vision: VISION-002
question: "Can swain simplify its deterministic layer by adopting agentrc's binary-backed primitives via agent-driven shell-out, without losing hackability?"
gate: Pre-MVP
swain-do: required
risks-addressed:
  - LLM drift on git, filesystem, and frontmatter mechanics embedded in skill prose
  - Parallel SPEC worktree coordination fragility across concurrent sessions
  - Duplicated frontmatter and worktree logic spread across many swain skills
trove: "docs/troves/agentrc-claude-orchestrator/"
linked-artifacts:
  - INITIATIVE-016
  - VISION-002
depends-on-artifacts: []
---

# Agentrc Primitives Adoption For Swain

## Summary

<!-- Final-pass section. Populate when transitioning to Complete.
     Lead with the verdict (Go / No-Go / Hybrid / Conditional). Follow with
     1-3 sentences that distill the key finding and recommended next step.
     Leave empty during Active phase — keep the document evidence-first. -->

## Question

Can swain simplify its deterministic layer by adopting agentrc's binary-backed primitives? The binary would be called by swain skills via shell-out. Operators still edit skill prose. This spike asks if the tradeoff is worth the cost.

## Go / No-Go Criteria

- **Go:** Two prototyped primitives (worktree lifecycle and topological integrate) prevent a documented set of drift failures pulled from recent retros. The prototype handles a parallel-SPEC scenario with two or more concurrent worktrees. Skill prose shrinks by a measurable amount when swain-do and swain-teardown call the binary.
- **No-Go:** Retros do not show enough mechanics drift to justify the binary's build and maintenance cost. Or the prototype couples too tightly to swain's artifact state machine. Or agentrc's gaps prove load-bearing for swain's use case.
- **Threshold:** The prototype must prevent at least three distinct drift failure modes drawn from the operator-sustainability log or retros. Skill prose must shrink by at least 100 lines across swain-do and swain-teardown combined. The parallel-SPEC scenario must merge cleanly or abort with a clear conflict report.

## Pivot Recommendation

If the prototype falls short: keep per-skill shell scripts. Harden the worst drift points with thin bash helpers rather than a unified binary. Revisit when swain has more concurrent SPECs and more skills that share mechanics.

## Findings

### Motivation

Swain today pushes deterministic work into skill prose. The LLM runs git commands, parses frontmatter, and manages worktrees step by step. As swain grows, drift and skipped steps tax the operator.

Agentrc shows a different approach. A Rust binary owns the deterministic work. A skill file tells the LLM what to build, not how to run git. The split holds even when you strip out agentrc's parallel-worker design.

The [agentrc trove synthesis](../../../troves/agentrc-claude-orchestrator/synthesis.md) covers the architecture in depth. Gap resolution for merge handling, observability, cost tracking, and the `voltagent-*` namespace is already captured there.

### Scope

The binary is agent-driven, not operator-driven. Swain skills shell out to it. Operators still patch skill files in plain text. They only rebuild the binary when mechanics change, not when judgment or phrasing changes.

Parallel SPECs are in scope. Swain operators run two or more concurrent worktrees often enough that the pattern is load-bearing. Any prototype must handle this case without manual coordination.

### Candidate Primitives

Five primitives from agentrc map to swain. The spike should prototype two of them end to end.

1. **Worktree lifecycle.** Port of `src/git/wrapper.rs` plus swain artifact-state checks. Commands: `swain worktree create|sync|merge|destroy <spec-id>`. The binary refuses operations on SPECs in invalid phases.
2. **Topological integrate.** Port of `src/commands/integrate.rs`. Merges concurrent worktree branches in dependency order. Detects file overlap across branches. Aborts cleanly on conflict.
3. **TDD commit audit.** Port of `src/commands/audit.rs`. Scans commit history for the red-green-refactor pattern. Gated by a `tdd_required: bool` frontmatter field so non-code artifacts are exempt.
4. **Frontmatter library.** Port of `src/fs/frontmatter.rs`. Commands: `swain fm get|set|validate`. Replaces ad-hoc yq, python, and sed calls across many skills.
5. **Event bus.** Port of `src/fs/bus.rs` and `src/commands/events.rs`. Append-only jsonl log. Unlocks auto-retros, roadmap regeneration, and drift timestamps.

### Non-Goals

- Full CLI replacement for swain skills.
- Adoption of tmux pane management (swain-helm is a separate scope).
- Solutions for agentrc's known gaps (merge recovery, cost tracking, `voltagent-*` references).
- A final choice of delivery language. The spike picks one (Rust, Go, or Python) and notes the tradeoff.

### Approach

1. Read the operator-sustainability log and recent retros. Count empirical failures that each primitive would have prevented. This grounds value ranking in evidence, not hunches.
2. Prototype two primitives end to end. Start with worktree lifecycle and topological integrate. These cover the parallel-SPEC case directly.
3. Wire swain-do and swain-teardown to call the prototype. Count lines of skill prose that become deletable.
4. Run a scenario with two or more concurrent worktree branches. Measure whether integrate's conflict detection catches file overlap cleanly.
5. Document the hackability impact. Which behaviors now need a rebuild? Which still live in prose?

### Evidence To Collect

- Drift failure count from retros, mapped to each primitive.
- Lines of skill prose that become deletable.
- Build and install friction, including toolchain cost and distribution via swain-init.
- Parallel-SPEC scenario throughput and conflict handling.
- Operator hackability check. Can the operator still change behavior by editing a file?

### Decision Criteria

- **Proceed** if prevented failure count justifies binary maintenance cost, parallel-SPEC workflow is measurably smoother, and hackability stays acceptable.
- **Defer** if retros show mechanics drift is rare, or the prototype reveals tight coupling to swain's artifact state model.
- **Abort** if agentrc's gaps prove load-bearing, requiring rework that exceeds fresh-build cost.

### Open Questions

- Which language fits best: Rust (reuse agentrc code directly), Go (cross-compile, fewer deps), or Python (matches swain's `uv`-based tooling)?
- How does the binary get installed on new machines? Homebrew, cargo install, or bundled via swain-init?
- Does the event bus introduce too much new state for solo operators who today work fine with markdown artifacts alone?

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-14 | — | Created from agentrc trove synthesis |
