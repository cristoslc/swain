---
title: "Session Recovery After Host Restart"
artifact: SPIKE-062
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
question: "When the host reboots and the host bridge daemon restarts, how does it reconcile its session registry with surviving tmux sessions, report dead sessions, and offer respawn?"
gate: Pre-Epic
parent-initiative: INITIATIVE-018
risks-addressed:
  - Host bridge restarts with stale session state, tries to route events to dead processes.
  - Tmux sessions survive reboot (persistent tmux) but the bridge lost their PIDs and state.
  - Operator sees phantom sessions in chat that no longer exist on the host.
evidence-pool: "process-supervision-patterns"
---

# Session Recovery After Host Restart

## Summary

## Question

When the host reboots and the host bridge daemon restarts, how does it reconcile its session registry with surviving tmux sessions, report dead sessions, and offer respawn?

### Context

The host bridge is a persistent daemon managed by launchd/systemd. When the host reboots, the daemon restarts automatically. But its in-memory session registry is gone. Tmux sessions may or may not have survived (depends on tmux server persistence config). Project bridge child processes are dead. The host bridge needs to:

1. Discover what tmux sessions still exist.
2. Match them against the last-known session registry (persisted to disk?).
3. Report dead sessions to the chat adapter.
4. Offer to respawn project bridges and re-adopt surviving sessions.
5. Handle the case where nothing survived (clean slate).

## Go / No-Go Criteria

- **Go:** A recovery sequence exists that correctly reconciles state in under 30 seconds with no operator intervention for the common case (clean reboot, all sessions dead).
- **No-Go:** Recovery requires operator decision-making for every session, or state reconciliation is unreliable.

## Pivot Recommendation

If automatic recovery is too complex, persist session state to a JSON file on every state change. On restart, read the file, diff against tmux reality, and present the operator with a reconciliation summary in the control thread. Manual but deterministic.

## Findings

_To be populated during research._

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Created from VISION-006 decomposition. |
