---
title: "A/B Subagent Eval for Behavioral Skill Instructions"
artifact: ADR-017
track: standing
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
linked-artifacts:
  - SPEC-173
  - SPEC-172
depends-on-artifacts: []
evidence-pool: ""
---

# A/B Subagent Eval for Behavioral Skill Instructions

## Context

Skill instructions that change agent behavior (e.g., "pause after GREEN and enumerate untested dimensions") cannot be verified by reading the file or running a linter. The instruction exists, but there's no evidence it works until an agent follows it. [SPEC-173](../../spec/Active/(SPEC-173)-TDD-Coverage-Self-Critique-Gate/(SPEC-173)-TDD-Coverage-Self-Critique-Gate.md) added a post-GREEN self-critique gate to `tdd-enforcement.md` — the only way to verify it was to observe whether an agent actually self-critiques when given the instructions.

Unit tests verify code. Behavioral evals verify instructions.

## Decision

Verify behavioral skill instructions using **A/B subagent evals**:

1. **Construct a scenario** — a realistic situation where the instruction should change behavior (e.g., "8 tests pass on a script with untested flags and fallback paths").
2. **Run agent A (control)** — a haiku subagent with the skill instructions *without* the new behavioral guidance. Record its response.
3. **Run agent B (treatment)** — same scenario, same model, but with the new behavioral guidance included. Record its response.
4. **Compare** — the treatment agent's response should exhibit the target behavior (e.g., enumerates untested dimensions). The control agent's response should not.

Both agents run in parallel for speed. The eval passes if the behavioral delta is observable — treatment does the thing, control doesn't.

### When to use

- Adding or modifying behavioral instructions in any skill file (SKILL.md, reference docs)
- The instruction is agent-facing guidance, not script logic
- The expected outcome is a change in agent behavior, not a change in file content

### When NOT to use

- Code changes with automated tests (use the tests)
- Skill routing changes (use the existing routing eval)
- Trivial wording fixes that don't change behavioral expectations

## Alternatives Considered

1. **Manual test in a new session** — start a fresh session, implement something, observe whether the agent self-critiques. Accurate but slow, non-repeatable, and conflates session state with the instruction's effect.
2. **Accept the limitation** — ship behavioral instructions without verification and observe in practice. Fast but provides no evidence before merge. The [SPEC-172](../../spec/Active/(SPEC-172)-Session-Bootstrap-Script-Consolidation/(SPEC-172)-Session-Bootstrap-Script-Consolidation.md) retro showed that "ship and observe" misses real bugs.
3. **Full eval harness (SPEC)** — build reusable tooling for behavioral evals. Valuable but premature — the A/B subagent pattern is simple enough to run ad-hoc until we know the eval shapes we need.

## Consequences

- **Positive:** Behavioral instructions now have a verification step before merge. The eval is cheap (two haiku subagent calls, ~10 seconds) and runs in the same session as the implementation.
- **Positive:** The A/B design isolates the instruction's effect — same scenario, same model, only the instruction differs.
- **Accepted downside:** Haiku may not perfectly simulate how Opus or Sonnet follow the instruction. The eval proves the instruction is *legible and actionable* to a model, not that every model follows it identically.
- **Accepted downside:** Scenario design is manual — the eval author must construct a scenario that makes the behavioral delta observable. Poor scenarios produce false passes.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Validated in SPEC-173 session: control skipped self-critique, treatment enumerated 5 gaps |
