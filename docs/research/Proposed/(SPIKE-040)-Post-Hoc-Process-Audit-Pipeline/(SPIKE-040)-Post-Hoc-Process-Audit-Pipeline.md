---
title: "Post-Hoc Process Audit Pipeline"
artifact: SPIKE-040
track: container
status: Proposed
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
question: "Can swain build a CI-integrated or commit-hook-integrated pipeline that validates process compliance after agent work completes, catching what PreToolUse hooks miss — and is this viable as the primary enforcement mechanism on platforms with weak hook support?"
gate: Pre-MVP
parent-initiative: INITIATIVE-020
risks-addressed:
  - PreToolUse hooks may not cover all platforms or all process rules
  - Post-hoc enforcement accepts process violations temporarily — operator must tolerate the gap
  - Audit pipeline may produce too many false positives to be actionable
evidence-pool: "platform-hooks-validation@21aa91c"
linked-artifacts:
  - SPIKE-038
  - VISION-005
---

# Post-Hoc Process Audit Pipeline

## Summary

## Question

Can swain build a CI-integrated or commit-hook-integrated pipeline that validates process compliance after agent work completes, catching what PreToolUse hooks miss — and is this viable as the primary enforcement mechanism on platforms with weak hook support?

## Go / No-Go Criteria

- **Go**: specwatch + design-check + a new process-compliance-check script can run in < 30 seconds as a pre-commit or CI step and catch the top 3 process violations (missing spec reference, skipped ADR check, lifecycle not updated)
- **No-Go**: Process compliance cannot be inferred from commit artifacts alone (requires session telemetry not available post-hoc)

## Pivot Recommendation

If post-hoc audit is insufficient, the enforcement strategy must be pre-execution only ([SPIKE-038](../../Active/(SPIKE-038)-PreToolUse-Hook-Adapter-Feasibility/(SPIKE-038)-PreToolUse-Hook-Adapter-Feasibility.md) + [SPIKE-039](../(SPIKE-039)-MCP-Session-State-Tracker-Design/(SPIKE-039)-MCP-Session-State-Tracker-Design.md)), accepting that platforms without good hook support get no enforcement. The alignment trove's "option 4: accept the gap" becomes the explicit fallback.

## Findings

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | 730b957 | Initial creation |
