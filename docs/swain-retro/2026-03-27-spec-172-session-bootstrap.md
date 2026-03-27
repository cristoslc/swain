---
title: "Retro: SPEC-172 Session Bootstrap Consolidation"
artifact: RETRO-2026-03-27-spec-172-session-bootstrap
track: standing
status: Active
created: 2026-03-27
last-updated: 2026-03-27
scope: "Single-session implementation of swain-session bootstrap consolidation"
period: "2026-03-26 — 2026-03-27"
linked-artifacts:
  - SPEC-172
  - SPIKE-046
  - EPIC-039
---

# Retro: SPEC-172 Session Bootstrap Consolidation

## Summary

Consolidated swain-session startup from 3-5 visible Bash tool calls into a single `swain-session-bootstrap.sh` invocation that emits structured JSON. Filed SPIKE-046 for a cross-skill audit of the same anti-pattern. Implementation completed in one session: design → spec → 24 tests → merge to trunk.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-172](../spec/Active/(SPEC-172)-Session-Bootstrap-Script-Consolidation/(SPEC-172)-Session-Bootstrap-Script-Consolidation.md) | Session Bootstrap Script Consolidation | Implemented, merged to trunk |
| [SPIKE-046](../research/Active/(SPIKE-046)-Noisy-Tool-Call-Pattern-Audit/(SPIKE-046)-Noisy-Tool-Call-Pattern-Audit.md) | Noisy Tool-Call Pattern Audit | Filed (Active), not yet investigated |

## Reflection

### What went well

- **Screenshot-driven design was efficient.** The operator showed the noisy startup output, the agent proposed three options (bootstrap script, path registry, well-known convention), the operator chose immediately, and work flowed from design → spec → implementation → merge without interruption.
- **TDD caught a real bug.** The jq fallback path — where jq exists on PATH but is non-functional — produced empty output. The test expansion phase caught this before it could surface in production. Without the operator's "what did you miss?" prompt, this would have shipped broken.
- **Spec-first discipline held.** Even for a single-session enhancement, having the SPEC with clear ACs meant the test harness could be written directly from the contract rather than reverse-engineered from the implementation.

### What was surprising

- **Initial test coverage was shallow despite appearing comprehensive.** 14 tests and 100% pass rate created false confidence. The operator's "how did you test it? what did you miss?" prompt revealed 6 untested dimensions: `--skip-worktree` flag, `lastBranch` write side-effect, jq unavailability, warnings population, idempotency, and main worktree detection. The agent was able to enumerate all gaps when asked directly — the knowledge was there, the self-critique wasn't.
- **The worktree branched from a stale release tag**, not trunk HEAD. The merge required a `git reset --hard trunk` to bring in the SPEC-172 artifact. The `EnterWorktree` tool creates branches from HEAD, which was a release tag — not the development tip. This is a known friction point with the worktree auto-isolation flow.

### What would change

- **Self-critique before claiming tests pass.** The agent should run through the "what did you miss?" exercise unprompted after writing tests, before declaring GREEN. The operator shouldn't need to be the one asking.
- **Test the operator experience, not just the contract.** Unit tests validated JSON output correctness but not the actual goal: fewer visible tool calls. An integration test (or at minimum, noting AC5 as requiring manual verification) should be part of the initial test plan.

### Patterns observed

- **"What did you miss?" is the highest-leverage operator intervention.** This is the second time this pattern has surfaced (see also SPEC-141 retro). When the agent is prompted to self-critique, it reliably identifies gaps it didn't surface proactively. This suggests a systematic weakness in the agent's completion-checking behavior.
- **The find-based script discovery pattern is pervasive.** Even the SKILL.md update for SPEC-172 still uses `find ... -path '*/scripts/swain-session-bootstrap.sh'` for the bootstrap invocation. SPIKE-046 exists to audit this, but the irony is visible: we shipped a fix for noisy discovery by adding another discoverable script.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_self_critique.md | feedback | Agent should self-critique test coverage before declaring GREEN |
