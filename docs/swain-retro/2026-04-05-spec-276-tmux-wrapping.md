---
title: "Retro: SPEC-286 bin/swain Missing Tmux Wrapping"
artifact: RETRO-2026-04-05-spec-276-tmux-wrapping
track: standing
status: Active
created: 2026-04-05
last-updated: 2026-04-05
scope: "Bugfix — bin/swain lost tmux wrapping when it replaced the shell function"
period: "2026-04-05"
linked-artifacts:
  - SPEC-286
  - SPEC-245
  - DESIGN-004
  - EPIC-056
---

# Retro: SPEC-286 bin/swain Missing Tmux Wrapping

## Summary

The shell launcher function `swain()` delegates to `bin/swain` via `exec` when it exists. [SPEC-245](../spec/Proposed/(SPEC-245)-Telemetry-Event-Emission-Framework/(SPEC-245)-Telemetry-Event-Emission-Framework.md) redesigned `bin/swain` as the worktree router but did not port the tmux wrapping logic from the shell function. The fix added tmux session creation (outside tmux), window renaming (inside tmux), and graceful fallback when tmux is not installed.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| [SPEC-286](../spec/Active/(SPEC-286)-bin-swain-Missing-Tmux-Wrapping/(SPEC-286)-bin-swain-Missing-Tmux-Wrapping.md) | bin/swain Missing Tmux Wrapping | Active — fix implemented, tests passing |

## Reflection

### What went well

- BDD test-first flow worked cleanly: 9 tests written and red, fix implemented, 9 tests green, zero regressions on the 10 existing tests.
- The existing `--_dry_run` flag made tmux behavior testable without spawning real sessions. Good prior investment in testability.
- Root cause was identified quickly by reading the launcher template and `bin/swain` side by side — the `exec bin/swain` short-circuit was obvious once you looked.

### What was surprising

- [DESIGN-004](../design/Active/(DESIGN-004)-swain-stage-Interaction-Design/(DESIGN-004)-swain-stage-Interaction-Design.md) explicitly shows "Rename tmux window" in its flow diagram, yet [SPEC-245](../spec/Proposed/(SPEC-245)-Telemetry-Event-Emission-Framework/(SPEC-245)-Telemetry-Event-Emission-Framework.md) has no AC for tmux behavior. The design documented the intent; the spec didn't capture it. The design-to-spec translation dropped a visible step.
- There are two artifacts with the ID DESIGN-004 — one Proposed ("bin/swain Worktree Router") and one Active ("swain-stage Interaction Design"). This is an ID collision that `next-artifact-id.sh` should have caught.

### What would change

- The spec for [SPEC-286](../spec/Active/(SPEC-286)-bin-swain-Missing-Tmux-Wrapping/(SPEC-286)-bin-swain-Missing-Tmux-Wrapping.md) was created on trunk's working tree before the worktree existed. This is the same pattern flagged in the 2026-04-03 retro (SPEC-251): file mutations landing on trunk instead of the worktree. The discipline is clear — create the worktree first, then write the spec inside it — but the swain-design skill doesn't enforce this because it doesn't know whether a worktree exists yet.
- When a DESIGN document describes a flow with named steps, those steps should map 1:1 to spec ACs or have an explicit "out of scope" note. A mechanical checklist during spec creation — "does the linked DESIGN have steps not covered by ACs?" — would have caught this.

### Patterns observed

- **Recurring: trunk mutations before worktree** — this is the second retro (after 2026-04-03 SPEC-251) where artifacts were written to trunk because the worktree didn't exist yet. The root cause is that swain-design runs before the operator creates a worktree.
- **Design-spec translation gap** — DESIGN flow diagrams are aspirational; SPECs are contractual. Steps in a DESIGN that aren't captured as ACs in a SPEC will be silently dropped during implementation.
- **Feature parity gap during redesign** — when a new implementation replaces an old one (`bin/swain` replacing the shell function), feature parity isn't guaranteed unless there's an explicit checklist of behaviors to port.

## SPEC candidates

1. **Design-to-spec AC coverage check** — when a SPEC links to a DESIGN, swain-design should cross-reference the DESIGN's flow steps against the SPEC's ACs and warn about uncovered steps. Prevents the translation gap that caused this bug.
2. **DESIGN-004 ID collision cleanup** — two artifacts share the ID DESIGN-004. One needs to be renumbered. This is a data integrity issue that `next-artifact-id.sh` should prevent.
3. **Worktree-before-mutation enforcement in swain-design** — when swain-design creates an artifact and no worktree is active (`SWAIN_WORKTREE_PATH` unset, not in a linked worktree), it should warn: "No worktree active — artifact will be created on trunk. Create a worktree first?" This addresses the recurring trunk-mutation pattern.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Design-to-spec AC coverage check | SPEC candidate | Cross-reference DESIGN flow steps against SPEC ACs to catch translation gaps |
| DESIGN-004 ID collision | SPEC candidate (data fix) | Two artifacts share DESIGN-004; renumber one |
| Worktree-before-mutation guard | SPEC candidate | swain-design should warn when creating artifacts without an active worktree |
| Trunk mutation pattern (recurring) | pattern | Second occurrence — 2026-04-03 and 2026-04-05 |
