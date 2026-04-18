---
title: "Automated Verification Loop"
artifact: INITIATIVE-022
track: container
status: Active
author: cristos
created: 2026-04-17
last-updated: 2026-04-17
parent-vision:
  - VISION-005
  - VISION-002
priority-weight: high
success-criteria:
  - Verification designs and runs on its own after implementation
  - Failed verification loops back, not to the operator
  - Teardown report saves agent decisions and results before merge
  - Report required before merge; review optional for small changes
  - Artifact alignment checks flag ADR, EPIC, and SPEC drift
  - prism-review agents run as part of verification
  - Supersedes EPIC-052 and EPIC-062; surviving parts reparented
  - Default loop limit (5 cycles, configurable) before escalation to operator
depends-on-artifacts:
  - EPIC-052
  - EPIC-062
addresses: []
evidence-pool: ""
---

# Automated Verification Loop

## Strategic Focus

Specs are written when the system is in one state. By the time implementation finishes, the system has moved on. ADRs were adopted. EPIC scope shifted. Other specs landed. Verification that runs against the original plan's assumptions is checking a world that no longer exists.

This initiative closes that gap. Verification design runs after implementation, against the current intent snapshot — not the snapshot from when the spec was written. The operator reviews results at teardown, not process during execution. The loop runs without human input, iterating until the work aligns with reality as it stands now.

This is urgent. It changes how swain builds things.

## Desired Outcomes

Agents verify against the system as it is now, not as it was when the spec was written. Verification design reads fresh artifact states — new ADRs, shifted EPIC scope, edited acceptance criteria — and checks whether the implementation still aligns. The operator reviews results at teardown, not process during execution. Small changes auto-merge with a saved report. Each cycle produces a retro. These pile up into a teardown narrative that shows the agent's decision trail.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**

- Two-phase execution: Implementation (swain-design, swain-do), then Verification (prism method, then execution).
- Verification design runs after implementation, using a fresh intent snapshot. This is the core insight: specs describe a prior state. Verification must run against the current state.
- Verification design has two jobs: discover existing tests that cover what changed, and write new tests for gaps. Both use the current intent snapshot, not the plan-time snapshot. Examples: BDD tests derived from Gherkin scenarios in specs (which may have evolved since the plan was written), ADR alignment checks that validate architectural fitness against active ADRs, and SPEC acceptance criteria coverage checks against the current criteria.
- Automated loop: failure triggers retro, then loops back to implementation.
- Reconciliation spectrum: small gap (add ticket), medium (update SPEC or ADR), large (escalate).
- Sensitivity scaling: small change to a sensitive module gets full verification; large low-risk change gets standard.
- Teardown report: agent decisions, verification history, test design, and results.
- Report required before trunk merge. Review optional for small changes.
- Retro after each cycle. Retros build the final teardown narrative.
- Retro captures agent decisions. Operator decisions come later.
- Artifact alignment: checks ADRs, EPIC scope, SPEC criteria.
- Supersedes EPIC-052 and EPIC-062. Surviving parts get reparented here.

**Out of scope:**

- Pre-implementation test design (replaced by post-implementation verification).
- Operator prompts during the loop (operator reviews at teardown only).
- Output formats for verification or retro (SPEC-level decisions).
- Gates in swain-sync or swain-release (replaced by teardown and loop).

## Supersession

| Superseded artifact | What survives | Where it lands |
|---------------------|---------------|----------------|
| [EPIC-052](../../../epic/Active/(EPIC-052)-Automated-Test-Gates/(EPIC-052)-Automated-Test-Gates.md) | verification-log.md, test detection, smoke from spec ACs | Reparented here |
| [EPIC-062](../../../epic/Active/(EPIC-062)-BDD-Traceability/(EPIC-062)-BDD-Traceability.md) | Gherkin rules, @bdd markers, sidecars, staleness checks | Reparented here |

Both EPICs move to Superseded. Child SPECs not absorbed stay under their EPICs until reparented.

## Tracks

**Track 1: Verification Design and Execution.** Prism as verification engine. Discovery of existing tests and writing of new ones. Sensitivity, scaling, the loop, reconciliation.

**Track 2: Teardown Report.** How the report captures history, decisions, and retros. Report mandatory; review optional for small changes.

**Track 3: Decision Logging and Retro.** Agent decisions during the loop. Per-cycle retros build a teardown narrative.

**Track 4: Artifact Alignment Agent.** Checks ADRs, EPIC scope, and SPEC criteria. May iterate per ADR or per batch.

**Track 5: Supersession Migration.** Move EPIC-052 and EPIC-062 to Superseded. Reparent SPECs. Update references.

## Child Epics

<!-- Updated as Epics are created under this initiative. -->

## Small Work (Epic-less Specs)

<!-- Specs attached directly to this initiative without an epic wrapper. -->

## Key Dependencies

- prism-review skill (methodology)
- swain-do completion (verification trigger)
- swain-teardown (report target)
- swain-retro (per-cycle and teardown)
- EPIC-052 and EPIC-062 child SPECs (reparenting)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-17 | — | Initial creation. Readability grade 10.1 after 5 revision attempts. |