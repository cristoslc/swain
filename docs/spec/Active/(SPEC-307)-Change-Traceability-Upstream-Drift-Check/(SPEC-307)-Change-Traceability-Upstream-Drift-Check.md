---
title: "Change traceability — auto-resolve upstream drift on edits"
artifact: SPEC-307
track: implementable
status: Active
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
priority-weight: ""
type: feature
parent-epic: ""
parent-initiative: ""
linked-artifacts:
  - SPIKE-070
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Change traceability — auto-resolve upstream drift on edits

## Problem Statement

Swain artifacts form a hierarchy: Vision → Initiative → Epic → Spec → Tickets. Today, changes at lower levels are not validated against their ancestors. A ticket edit can drift away from its parent SPEC. A SPEC edit can drift away from its parent EPIC, Initiative, or Vision. The operator has no signal that a change at one layer contradicts or drifts from decisions recorded above it.

This is a traceability gap. Swain's Intent → Execution → Evidence → Reconciliation loop requires that execution (tickets, SPECs) stays aligned with intent (EPICs, Visions). Without an upstream check, drift accumulates silently until a retro or audit surfaces it — often too late to correct cheaply.

## Desired Outcomes

- Edits to tickets and SPECs trigger an automatic drift resolution pass. The agent compares the child against its parent and proposes a fix: either edit the child to re-align, or edit the parent to accept the change.
- The agent picks child vs. parent based on signals — primarily the count of prior drift conflicts recorded against the parent. More conflicts against a parent suggest the parent itself needs updating, not the child.
- The operator reviews the agent's choices, not raw warnings. The operator can accept, modify, or dismiss each proposed fix.
- Drift resolution is recorded as a decision for future signal accumulation.
- Work batches keep moving. The check proposes fixes; it does not block.

## External Behavior

**Drift detection.** When a ticket is created, edited, or closed under a SPEC, or when a SPEC is created, edited, or transitions phase under a parent object, the skill runs a drift check. It reads both the child and parent artifacts, compares the child's scope and acceptance criteria against the parent's goals and constraints, and identifies any misalignment.

**Auto-resolution.** For each detected drift, the agent chooses one of two fixes:

1. **Child fix** — edit the child to re-align with the parent.
2. **Parent fix** — edit the parent to accept the child's change.

The agent's choice is driven by **both structured signals and content judgment**. Structured signals include the count of prior drift conflicts recorded against the parent (more conflicts → parent is likelier stale). Content judgment comes from the agent reading both artifacts and assessing which direction produces the better outcome — e.g., whether the child's change is a natural extension the parent should absorb, or whether the child overreached and should be narrowed. The agent explains its reasoning in each case.

**Fixes are applied, not proposed.** The agent implements the chosen fix (edits the artifact on disk) and then presents what it did for operator review. The operator can accept, modify, or revert each fix.

**Review presentation.** After the resolution pass, the agent presents a summary of its actions:

```
Drift resolution for <CHILD-ID> against <PARENT-ID>:
  [parent fix ← applied] Broadened SPEC-100 AC-2 to include OAuth2
    Reason: 4 prior conflicts against <PARENT-ID>, and OAuth2 is
    a natural extension of the auth scope described in the EPIC goals.
  Accept / modify / revert?
```

The operator can accept all, modify individual fixes, or revert. Reverts are recorded as decisions for future signal weighting.

**No drift check on unparented objects.** If a SPEC has no parent EPIC, Initiative, or Vision, no upstream drift check runs (no parent to check against).

**No drift check on ephemeral objects.** Tickets are ephemeral (ADR-015). The check runs because tickets are where drift is most likely to enter, but the check result is advisory only and does not create a formal artifact.

## Acceptance Criteria

**Given** a ticket created under SPEC-100 with description "Add OAuth2 login flow",
**When** SPEC-100's acceptance criteria only cover "local password auth",
**Then** the agent detects drift, applies a child fix (narrows the ticket) or parent fix (broadens the SPEC) based on signals and content judgment, and presents the applied fix for review.

**Given** a ticket edited to change its scope,
**When** the new scope falls within the parent SPEC's acceptance criteria,
**Then** no drift is detected and no resolution is applied.

**Given** a SPEC edited to add a new acceptance criterion,
**When** the new criterion is not derivable from the parent EPIC's goals or success criteria,
**Then** the agent applies a child fix or parent fix based on signal weight and content judgment, and presents the result for review.

**Given** a parent with accumulated drift conflicts and a child that introduces a natural extension of the parent's goals,
**When** the agent evaluates both directions,
**Then** the agent applies a parent fix, citing both the conflict count and its content assessment.

**Given** a parent with few conflicts and a child that overreaches beyond the parent's scope,
**When** the agent evaluates both directions,
**Then** the agent applies a child fix, citing both the low conflict count and its content assessment.

**Given** the operator accepts the agent's applied resolution,
**When** the fix is already on disk,
**Then** a drift decision is recorded in the session log and the fix stands.

**Given** the operator reverts a resolution,
**When** the revert is applied and recorded,
**Then** the artifact is restored, the session log contains a decision entry, and the conflict count for that parent is incremented for future signal weighting.

**Given** the AGENTS.md "Change traceability" section,
**When** an operator reads it,
**Then** it describes the auto-resolve model (drift detected → fix applied → reviewed), signal-based direction (conflict count + content judgment), and the three operator outcomes (accept, modify, revert) in under 80 words.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope.**

- Ticket → SPEC drift check in swain-do (on ticket create, edit, close).
- SPEC → parent drift check in swain-design (on SPEC create, edit, phase transition).
- Auto-resolution: agent applies child fix or parent fix based on signals + content judgment.
- Review presentation: operator reviews applied fixes, can accept, modify, or revert.
- Drift decision recording in session log for signal accumulation.
- Conflict count derivation from recorded drift decisions.

**Out of scope.**

- EPIC → Initiative or Vision drift check. Runs during audits only, not on every edit.
- Drift detection across sibling SPECs or sibling EPICs.
- A fix applied without operator review.

**Constraints.**

- Checks must complete in under 2 seconds for typical artifacts.
- The agent applies fixes first, then presents for review — never asks permission before acting.
- The check uses the artifact content on disk, not an external service.
- Conflict counts are derived from recorded drift decisions, not a separate counter file.

## Implementation Approach

1. **Build a drift detection function.** Takes a child artifact path and a parent artifact path. Reads both. Compares child scope/acceptance criteria against parent goals/success criteria/constraints. Returns aligned, drifted (with drift description), or no-parent. Ship as a script under `.swain/bin/`.
2. **Build conflict count lookup.** Read the session log and artifact notes for prior drift decisions mentioning the parent. Count conflicts. Return the count.
3. **Wire auto-resolution into swain-do.** On ticket create/edit/close, if the ticket has a `spec:` tag, run drift detection. If drifted, apply child fix or parent fix based on conflict count and content judgment. Present applied fix for review. On operator accept, record decision. On revert, undo the edit and increment conflict count.
4. **Wire auto-resolution into swain-design.** On SPEC create/edit/transition, if the SPEC has a parent, run drift detection. Same resolution and review logic.
5. **Record decisions.** On every resolution (accept, modify, revert), call `swain-session-state.sh record-decision` with the parent ID and fix direction. This feeds future conflict counts.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Initial creation |