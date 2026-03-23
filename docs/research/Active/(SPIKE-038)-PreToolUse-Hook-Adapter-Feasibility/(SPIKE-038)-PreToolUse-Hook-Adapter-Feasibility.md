---
title: "PreToolUse Hook Adapter Feasibility"
artifact: SPIKE-038
track: container
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
question: "Can swain implement process governance gates (spec-read check, ADR compliance, skill invocation mandate) via PreToolUse hooks on each target platform, and what does the adapter look like?"
gate: Pre-MVP
parent-initiative: INITIATIVE-020
risks-addressed:
  - Hook APIs may not expose enough context for process-aware validation
  - Subagent coverage gaps (OpenCode #5894) may undermine enforcement
  - Per-platform adapter maintenance may be unsustainable
evidence-pool: "platform-hooks-validation@21aa91c"
linked-artifacts:
  - SPIKE-039
  - VISION-005
---

# PreToolUse Hook Adapter Feasibility

## Summary

## Question

Can swain implement process governance gates (spec-read check, ADR compliance, skill invocation mandate) via PreToolUse hooks on each target platform, and what does the adapter look like?

## Go / No-Go Criteria

- **Go**: At least 2 platforms support PreToolUse hooks with enough context (tool name, arguments, and ideally session state) to implement a "block commit unless ADR check passed" gate
- **No-Go**: PreToolUse hooks are too coarse (no argument inspection) or too fragile (breaking API changes) to build reliable process gates on any platform

## Pivot Recommendation

If PreToolUse is insufficient, pivot to post-hoc audit only ([SPIKE-040](../../Proposed/(SPIKE-040)-Post-Hoc-Process-Audit-Pipeline/(SPIKE-040)-Post-Hoc-Process-Audit-Pipeline.md)) and accept that enforcement is reactive rather than preventive. Alternatively, investigate MCP-server-side validation (intercept tool calls at the MCP layer rather than the platform hook layer).

## Findings

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | 730b957 | Initial creation |
| Active | 2026-03-23 | 9293866 | Activated for Claude Code hook testing |
