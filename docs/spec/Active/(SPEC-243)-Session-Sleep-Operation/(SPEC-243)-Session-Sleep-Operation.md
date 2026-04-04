---
title: "Session Sleep Operation"
artifact: SPEC-243
track: implementable
status: Active
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
priority-weight: ""
type: feature
parent-epic: ""
parent-initiative: INITIATIVE-019
linked-artifacts:
  - ADR-018
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Session Sleep Operation

## Problem Statement

When the operator steps away, the agent either idles (wasting time) or requires the operator to explicitly queue work before leaving. There is no mechanism for the agent to continue working autonomously within safe boundaries, track time, or enforce the operator's stated break duration.

## Desired Outcomes

The operator can say "sleep, back in 2 hours" and walk away. The agent continues productive work within risk-tiered boundaries, writes a checkpoint summary at the return time, and enforces the operator's break — refusing to engage if the operator returns early. This supports operator sustainability by preventing compulsive check-ins.

## External Behavior

**Input:** Operator says "sleep", "I'm stepping away", "work while I'm gone", "keep going, back in 2 hours."

**Entry sequence:**
1. Agent asks: "When will you be back?"
2. Agent runs `swain-session-sleep.sh start <ISO-return-time>` to atomically record sleep state to `session.json`
3. Agent acknowledges: "Got it. Working until `<time>`. Safe to walk away."

**During sleep — risk tiers:**

| Tier | Actions | Behavior |
|------|---------|----------|
| Autonomous | Write code, run tests, commit to worktree, transition artifacts, claim/close tk tasks, create worktrees, bookmark updates | Proceed without pause |
| Deferred | Push, merge to trunk, create PRs, create/close GitHub issues, post external comments, delete branches | Log to `sleep.deferredActions` array in session.json |

**Work prioritization (soft constraints):**
1. Finish current in-progress tk tasks
2. Claim and execute ready tasks in the current plan
3. If plan exhausts, pick up ready specs in the focus lane
4. If focus lane exhausts, idle with checkpoint

**Checkpoint:** At `returnBy` time, agent writes a summary to `docs/swain-retro/sleep-summary-<date>.md`, opens it for the operator, then continues working on autonomous-tier actions.

**Break enforcement:** If the operator sends input before `returnBy`, the `UserPromptSubmit` hook blocks it with exit code 2 and a message. Ctrl-C is the only override.

**Stop hook:** On every turn during sleep, the hook evaluates checkpoint status deterministically and injects `{"decision": "continue"}` or `{"decision": "checkpoint"}` into the context stream. The hook atomically sets `checkpointDone: true` in session.json before outputting the checkpoint decision (preventing duplicate checkpoints across rapid turns).

## Acceptance Criteria

- **AC-1:** Given the operator says "sleep, back in 2 hours", when sleep state is recorded, then `session.json` contains `sleep.start`, `sleep.returnBy` (absolute ISO), `sleep.checkpointDone: false`, and `sleep.deferredActions: []`.
- **AC-2:** Given sleep mode is active, when the agent encounters a deferred-tier action (push, merge, PR), then it logs the action to `sleep.deferredActions` and does not execute it.
- **AC-3:** Given sleep mode is active and the operator sends a message before `returnBy`, then the `UserPromptSubmit` hook blocks it with exit code 2 and a refusal message.
- **AC-4:** Given sleep mode is active and current time >= `returnBy`, when the operator sends a message, then the hook clears sleep state and allows the prompt through.
- **AC-5:** Given sleep mode is active and the Stop hook detects time >= `returnBy` with `checkpointDone: false`, then it atomically sets `checkpointDone: true` and injects `{"decision": "checkpoint"}`.
- **AC-6:** Given the agent receives a checkpoint decision, then it writes a summary to `docs/swain-retro/sleep-summary-<date>.md` and continues working.
- **AC-7:** On runtimes without `UserPromptSubmit` hooks, break enforcement degrades to behavioral-only (skill prose instructs agent to refuse).

## Scope & Constraints

- Claude Code hooks first. Other runtimes degrade to behavioral enforcement per [ADR-018](../../../adr/Active/(ADR-018)-Structural-Not-Prosaic-Session-Invocation/(ADR-018)-Structural-Not-Prosaic-Session-Invocation.md).
- Hook commands must use `find`-based script discovery to work from worktrees.
- Risk classification (autonomous vs deferred) is judgment — lives in skill prose, not scripts.
- Work prioritization is soft (plan first, then focus lane) — not a hard constraint.
- swain-init installs the hooks during onboarding; they are no-ops when sleep state is absent.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-28 | — | Initial creation from brainstorming design |
